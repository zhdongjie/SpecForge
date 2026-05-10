from __future__ import annotations

import argparse
import json
import re
import sys
from hashlib import pbkdf2_hmac
from pathlib import Path

import yaml


DEMO_ACCOUNTS = [
    {"username": "Admin", "password": "Admin@123456"},
    {"username": "User", "password": "User@123456"},
]
PBKDF2_ITERATIONS = 310000
PBKDF2_SALT_HEX = "00112233445566778899aabbccddeeff"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export delivery assets for generated SpecForge backends.")
    parser.add_argument("--backend-root", required=True)
    parser.add_argument("--base-url", default="http://localhost:8080/api")
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_passwords(yaml_text: str) -> tuple[str, str]:
    passwords = re.findall(r"^\s*password\s*:\s*([^\s#]+)", yaml_text, re.MULTILINE)
    if not passwords:
        return "root", "root"
    if len(passwords) == 1:
        return passwords[0], passwords[0]
    return passwords[0], passwords[1]


def pbkdf2_password(password: str) -> str:
    salt = bytes.fromhex(PBKDF2_SALT_HEX)
    derived = pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS, dklen=32)
    return "{pbkdf2}" + (salt + derived).hex()


def build_demo_access(base_url: str, datasource_password: str, redis_password: str) -> dict[str, object]:
    return {
        "status": "READY",
        "base_url": base_url,
        "login_endpoint": f"{base_url.rstrip('/')}/v1/authorize/login",
        "refresh_token_endpoint": f"{base_url.rstrip('/')}/v1/authorize/refresh-token",
        "seed_sql": "src/main/resources/sql/schema.sql",
        "demo_password_reset_sql": "src/main/resources/sql/demo-password-reset.sql",
        "postman_collection": "logs/api-smoke/postman-collection.json",
        "postman_environment": "logs/api-smoke/postman-environment.json",
        "curl_login_script": "logs/api-smoke/curl-login-example.sh",
        "powershell_login_script": "logs/api-smoke/invoke-login.ps1",
        "database_defaults": {
            "username": "root",
            "password": datasource_password,
        },
        "redis_defaults": {
            "password": redis_password,
        },
        "demo_accounts": DEMO_ACCOUNTS,
        "notes": [
            "Import schema.sql first, then apply demo-password-reset.sql to guarantee known login passwords.",
            "Import postman-environment.json together with postman-collection.json for quick API smoke validation.",
            "Treat this file as the primary handoff entrypoint for frontend and interface testing.",
        ],
    }


def write_postman_environment(path: Path, base_url: str) -> None:
    payload = {
        "name": "SpecForge Generated Backend Local",
        "values": [
            {"key": "baseUrl", "value": base_url, "enabled": True},
            {"key": "username", "value": DEMO_ACCOUNTS[0]["username"], "enabled": True},
            {"key": "password", "value": DEMO_ACCOUNTS[0]["password"], "enabled": True},
            {"key": "accessToken", "value": "", "enabled": True},
        ],
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def write_demo_password_reset_sql(path: Path) -> None:
    lines = [
        "-- SpecForge deterministic demo password reset",
        "-- Apply after schema.sql import to guarantee known demo login credentials.",
        "",
    ]
    for account in DEMO_ACCOUNTS:
        lines.append(
            "UPDATE `system_user`"
            f" SET `encoded_password` = '{pbkdf2_password(account['password'])}'"
            f" WHERE `username` = '{account['username']}';"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_curl_script(path: Path, base_url: str) -> None:
    payload = json.dumps(
        {"username": DEMO_ACCOUNTS[0]["username"], "password": DEMO_ACCOUNTS[0]["password"]},
        ensure_ascii=False,
    )
    lines = [
        "#!/usr/bin/env sh",
        "set -e",
        "",
        f"BASE_URL=\"{base_url.rstrip('/')}\"",
        "curl -X POST \"$BASE_URL/v1/authorize/login\" \\",
        "  -H \"Content-Type: application/json\" \\",
        f"  -d '{payload}'",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_powershell_script(path: Path, base_url: str) -> None:
    lines = [
        "$baseUrl = \"" + base_url.rstrip("/") + "\"",
        "$body = @{",
        "  username = \"" + DEMO_ACCOUNTS[0]["username"] + "\"",
        "  password = \"" + DEMO_ACCOUNTS[0]["password"] + "\"",
        "} | ConvertTo-Json",
        "",
        "Invoke-RestMethod -Method Post -Uri ($baseUrl + \"/v1/authorize/login\") -ContentType \"application/json\" -Body $body",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    output_root = Path(args.backend_root).resolve()
    resources_root = output_root / "src" / "main" / "resources"
    logs_root = output_root / "logs"
    api_smoke_root = logs_root / "api-smoke"
    api_smoke_root.mkdir(parents=True, exist_ok=True)

    app_yaml_path = resources_root / "application.yaml"
    app_yaml_text = read_text(app_yaml_path) if app_yaml_path.exists() else ""
    datasource_password, redis_password = extract_passwords(app_yaml_text)

    demo_access = build_demo_access(args.base_url, datasource_password, redis_password)
    (logs_root / "demo-access.yaml").write_text(
        yaml.safe_dump(demo_access, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    write_postman_environment(api_smoke_root / "postman-environment.json", args.base_url)
    write_demo_password_reset_sql(resources_root / "sql" / "demo-password-reset.sql")
    write_curl_script(api_smoke_root / "curl-login-example.sh", args.base_url)
    write_powershell_script(api_smoke_root / "invoke-login.ps1", args.base_url)

    report = {
        "status": "PASS",
        "output_root": str(output_root),
        "artifacts": [
            "logs/demo-access.yaml",
            "logs/api-smoke/postman-environment.json",
            "logs/api-smoke/curl-login-example.sh",
            "logs/api-smoke/invoke-login.ps1",
            "src/main/resources/sql/demo-password-reset.sql",
        ],
    }
    (logs_root / "delivery-assets-report.yaml").write_text(
        yaml.safe_dump(report, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    sys.stdout.write(json.dumps(report, indent=2, ensure_ascii=False))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

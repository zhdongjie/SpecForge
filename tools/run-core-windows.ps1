[CmdletBinding()]
param(
    [string]$Distribution = 'Ubuntu',
    [string]$RepoRoot = '/home/zhang/projects/ai/SpecForge',
    [string]$Template = '/mnt/e/Project/Zhang/openclaw-codegen/templates/admin-platform',
    [string]$Workspace = '/home/zhang/.local/state/specforge-core/device-borrow',
    [string]$Spec = '',
    [string]$AcceptancePack = 'device-borrow',
    [string]$Node = '',
    [string]$PlaywrightModule = '',
    [string]$Chromium = 'C:/Program Files/Google/Chrome/Application/chrome.exe',
    [switch]$ReuseBuild
)
$ErrorActionPreference = 'Stop'
function Quote-Bash([string]$Value) { return "'" + $Value.Replace("'", "'\''") + "'" }
$sfBundle = Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/node'
if (-not $Node) { $Node = Join-Path $sfBundle 'bin/node.exe' }
if (-not $PlaywrightModule) { $PlaywrightModule = Join-Path $sfBundle 'node_modules/playwright' }
if (-not $Spec) { $Spec = "$RepoRoot/examples/device_borrow.yaml" }
foreach ($sfPath in @($Node,$PlaywrightModule,$Chromium)) {
    if (-not (Test-Path -LiteralPath $sfPath)) { throw "Missing browser dependency: $sfPath" }
}
$sfStaging = Join-Path $env:TEMP ('specforge-browser-' + [Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $sfStaging | Out-Null
$sfWorkerFile = Join-Path $sfStaging 'browser-worker.cjs'
$sfWorkerText = & wsl.exe -d $Distribution -- bash -lc ('cat ' + (Quote-Bash "$RepoRoot/specforge/assets/browser-worker.cjs"))
if ($LASTEXITCODE -ne 0) { throw 'Cannot read SpecForge browser worker' }
[IO.File]::WriteAllText($sfWorkerFile,($sfWorkerText -join "`n"),[Text.UTF8Encoding]::new($false))
$sfNativeStaging = $sfStaging.Replace('\','/')
$sfLinuxStaging = (& wsl.exe -d $Distribution -- wslpath -u $sfNativeStaging).Trim()
$sfLinuxNode = (& wsl.exe -d $Distribution -- wslpath -u $Node.Replace('\','/')).Trim()
$sfWorker = Start-Process -FilePath $Node -ArgumentList @("`"$sfWorkerFile`"","`"$sfStaging`"") -WindowStyle Hidden -PassThru
try {
    $sfSetup = 'set -euo pipefail; cd ' + (Quote-Bash $RepoRoot) + '; export JAVA_HOME="$HOME/.sdkman/candidates/java/current"; export PATH="$JAVA_HOME/bin:$HOME/.sdkman/candidates/maven/current/bin:$HOME/.nvm/versions/node/v24.15.0/bin:$PATH"; export DOCKER_BUILDKIT=0; '
    $sfVars = @{
        SPECFORGE_BROWSER_NODE = $sfLinuxNode
        SPECFORGE_PLAYWRIGHT_MODULE = $PlaywrightModule.Replace('\','/')
        SPECFORGE_CHROMIUM_EXECUTABLE = $Chromium.Replace('\','/')
        SPECFORGE_BROWSER_QUEUE = '1'
        SPECFORGE_BROWSER_STAGING = $sfLinuxStaging
    }
    foreach ($sfEntry in $sfVars.GetEnumerator()) { $sfSetup += 'export ' + $sfEntry.Key + '=' + (Quote-Bash $sfEntry.Value) + '; ' }
    if ($ReuseBuild) {
        $sfCommand = 'python3 -m specforge verify --reuse-build --workspace ' + (Quote-Bash $Workspace)
    } else {
        $sfCommand = 'python3 -m specforge run --workspace ' + (Quote-Bash $Workspace) + ' --spec ' + (Quote-Bash $Spec) + ' --template ' + (Quote-Bash $Template)
    }
    $sfCommand += ' --acceptance-pack ' + (Quote-Bash $AcceptancePack)
    & wsl.exe -d $Distribution -- bash -lc ($sfSetup + $sfCommand)
    $sfResult = $LASTEXITCODE
} finally {
    if (-not $sfWorker.HasExited) { Stop-Process -Id $sfWorker.Id }
    # Remove only this invocation's freshly created temporary staging directory.
    $sfResolved = [IO.Path]::GetFullPath($sfStaging)
    $sfTempRoot = [IO.Path]::GetFullPath($env:TEMP).TrimEnd('\') + '\'
    if (-not $sfResolved.StartsWith($sfTempRoot,[StringComparison]::OrdinalIgnoreCase)) { throw 'Unexpected staging path' }
    Remove-Item -LiteralPath $sfResolved -Recurse -Force
}
exit $sfResult

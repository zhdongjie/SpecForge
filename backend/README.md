# Original Keen Auth Center

## Project Overview

Original Keen Auth Center is a backend service framework based on Spring Boot, providing complete user authentication, permission
management, file processing, and logging functionality. The project adopts a modern Java development technology stack,
follows RESTful API design specifications, and provides secure and efficient backend support for frontend applications.

## Technology Stack

- **Core Framework**: Spring Boot 3.4.4
- **Security Framework**: Spring Security
- **Data Access**: MyBatis-Flex
- **Database**: MySQL
- **Cache**: Redis
- **Authentication**: JWT (Jose4j)
- **Build Tool**: Maven

## Project Structure

```
src/main/java/com/original/
├── authorize        # Authentication module
├── business         # Business functionality module
│   └── personal     # Personal center business
├── core             # Core functionality module
│   ├── annotation   # Custom annotations
│   ├── aspectj      # AOP aspects
│   ├── config       # Configuration classes
│   ├── constant     # Constants
│   ├── domain       # Domain models
│   ├── enums        # Enumeration types
│   ├── exception    # Exception handling
│   ├── manager      # Managers
│   ├── service      # Service interfaces
│   └── utils        # Utility classes
└── system           # System management module
    ├── log          # Log management
    ├── permission   # Permission management
    ├── role         # Role management
    └── user         # User management
```

## Functional Modules

### Authentication Module

- User registration
- User login
- JWT token management
- Permission verification

### System Management Module

- User management: CRUD operations for users, import and export
- Role management: CRUD operations for roles, permission assignment
- Permission management: CRUD operations for permissions, permission tree structure
- Log management: Access logs, operation logs recording and querying

### Business Functionality Module

- Personal center: View personal information, password modification

## Development Environment Requirements

- JDK 17+
- Maven 3.8+
- MySQL 8.0+
- Redis 6.0+
- IDE: IntelliJ IDEA recommended

## Quick Start

### 1. Clone the Project

```bash
git clone https://github.com/joel-shi-cnc/original-service.git
cd original-service
```

### 2. Configure Database

- Create MySQL database: `original`
- Execute SQL script: `src/main/resources/sql/schema.sql`

### 3. Configure Application

Modify database and Redis connection information in `src/main/resources/application.yaml`:

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/original?characterEncoding=UTF-8&serverTimezone=Asia/Shanghai
    username: [ your_database_username ]
    password: [ your_database_password ]
  data:
    redis:
      host: [ Redis_host_address ]
      port: 6379
      password: [ Redis_password ]
```

### 4. Build and Run

```bash
mvn clean package
java -jar target/original-service-0.0.1-SNAPSHOT.jar
```

Or run using Maven plugin:

```bash
mvn spring-boot:run
```

### 5. Access API

After the application starts, you can access the API through the following addresses:

- API base path: `http://localhost:8080/api`
- Authentication interface: `http://localhost:8080/api/v1/authorize`

## Contribution Guidelines

1. Fork this repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add some amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Submit a Pull Request

## Commenting Guidelines

The project follows strict commenting guidelines, see `document/CommentingGuidelines.md` file for details.

## License

[Add license information]

## Contact

[Add contact information]

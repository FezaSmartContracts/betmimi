
# Project Structure

```bash
.
├── Dockerfile                        # Dockerfile for building the application container.
├── docker-compose.yml                # Docker Compose file for defining multi-container applications.
├── pyproject.toml                    # Poetry configuration file with project metadata and dependencies.
├── README.md                         # Project README providing information and instructions.
├── LICENSE.md                        # License file for the project.
├── wait-for-it.sh                       
│
│
└── src                               # Source code directory.
    ├── __init__.py                   # Initialization file for the src package.
    ├── alembic.ini                   # Configuration file for Alembic (database migration tool).
    ├── poetry.lock                   # Poetry lock file specifying exact versions of dependencies.
    │
    ├── app                           # Main application directory.
    │   ├── __init__.py               # Initialization file for the app package.
    │   ├── main.py                   # Main entry point of the FastAPI application.
    │   │
    │   │
    │   ├── api                       # Folder containing API-related logic.
    │   │   ├── __init__.py
    │   │   ├── dependencies.py       # Defines dependencies for use across API endpoints.
    │   │   │
    │   │   ├── general                    # Non-contract specific endpoints e.g for user login.
    │   │   │   ├── __init__.py
    │   │   │   ├── admin.py             # API route for administration.
    │   │   │   ├── connect_wallet.py    # API route for wallet connections.
    │   │   │   ├── disconnect_wallet.py # API routes for wallet disconnections.
    │   │   │   ├── games.py             # API routes for the `GamesManager` contract.
    │   │   │   ├── rate_limits.py       # API routes for rate limiting functionalities.
    │   │   │   └── users.py             # API routes for user management.
    │   │   │  
    │   │   └── usdtv1              # USDT specific endpoints.
    │   │       ├── __init__.py     
    │   │       ├── predictions.py  # API route for all prediction related endpoints.
    │   │       └── tasks.py        # API routes for tasks
    │   │
    │   │
    │   ├── core                        # Core utilities and configurations for the application.
    │   │   ├── __init__.py
    │   │   ├── address_verification.py # Utiliy for address verification during connections
    │   │   ├── config.py               # Configuration settings for the application.
    │   │   ├── logger.py               # Configuration for application logging.
    │   │   ├── schemas.py              # Pydantic schemas for data validation.
    │   │   ├── security.py             # Security utilities, such as password hashing.
    │   │   ├── setup.py                # Setup file for the FastAPI app instance.
    │   │   │
    │   │   ├── akabokisi             # Mailbox management moule.
    │   │   │   ├── __init__.py
    │   │   │   ├── static            # Folder for static files e.g Images
    │   │   │   ├── templates         # Emal templates folder
    │   │   │   ├── helper.py         # Moodule-specifc helper functions
    │   │   │   ├── manager.py        # Core email management class
    │   │   │   ├── messages.py       # mail message strings.
    │   │   │   └── topics.py         # Essentiial diict
    │   │   │
    │   │   ├── artifacts                 # Contracts artifacts
    │   │   │   └── arbitrum              # folder for arbitrum specific artifacts
    │   │   │   
    │   │   ├── db                    # Core Database related modules.
    │   │   │   ├── __init__.py
    │   │   │   ├── crud_token_blacklist.py  # CRUD operations for token blacklist.
    │   │   │   ├── database.py       # Database connectivity and session management.
    │   │   │   ├── models.py         # Core Database models.
    │   │   │   └── token_blacklist.py  # Model for token blacklist functionality.
    │   │   │
    │   │   ├── exceptions            # Custom exception classes.
    │   │   │   ├── __init__.py
    │   │   │   ├── cache_exceptions.py   # Exceptions related to cache operations.
    │   │   │   └── http_exceptions.py    # HTTP-related exceptions.
    │   │   │
    │   │   ├── utils                 # Utility functions and helpers.
    │   │   │   ├── __init__.py
    │   │   │   ├── cache.py          # Cache-related utilities.
    │   │   │   ├── queue.py          # Utilities for task queue management.
    │   │   │   └── rate_limit.py     # Rate limiting utilities.
    │   │   │
    │   │   ├── web3_services         # web3 connection moule.
    │   │   │   ├── __init__.py
    │   │   │   ├── arbitrum_one      # arbitrum-specific module.
    │   │   │   │   ├─ __init__.py
    │   │   │   │   ├── handlers      # event handlers module.
    │   │   │   │   │   ├─ alerts.py  # System notifications.
    │   │   │   │   │   ├─ helper.py  # helper functions.
    │   │   │   │   │   └── usdtv1.py # Usdt-specific event handler methods.
    │   │   │   │   │
    │   │   │   │   ├── callbacks.py  # central callbacks collection.
    │   │   │   │   ├── event_topics.py # event topics dict.
    │   │   │   │   ├── functions.py # helper functions.
    │   │   │   │   ├── handler.py # manages a dictionary of callables.
    │   │   │   │   └── websocket_service.py # # Class to manage websocket.
    │   │   │   │
    │   │   │   ├── get_functions  # GET functions from contracts
    │   │   │   │   ├── usdt       # usdt specific contracts get functions folder.
    │   │   │   │   │   └── functions.py
    │   │   │   │   └── manager.py # Http connections manager.
    │   │   │   │             
    │   │   │   ├── fallback_manager.py   # Emergency/fallback management class.
    │   │   │   ├── manager.py         # Websocket Subscriptions handler class.
    │   │   │   ├── processor.py       # central processor for application data.
    │   │   │   └── utils.py           # utilities file.
    │   │   │
    │   │   └── worker                # Worker script for background tasks.
    │   │       ├── __init__.py
    │   │       ├── settings.py       # Worker configuration and settings.
    │   │       └── functions.py      # Async task definitions and management.
    │   │
    │   ├── crud                      # CRUD operations for the application.
    │   │   ├── __init__.py
    │   │   ├── crud_base.py          # Base class for CRUD operations.
    │   │   ├── crud_posts.py         # CRUD operations for posts.
    │   │   ├── crud_rate_limit.py    # CRUD operations for rate limiting.
    │   │   ├── crud_tier.py          # CRUD operations for user tiers.
    │   │   ├── crud_users.py         # CRUD operations for users.
    │   │   └── helper.py             # Helper functions for CRUD operations.
    │   │
    │   ├── logs                      # Directory for log files.
    │   │   └── app.log               # Log file for the application.
    │   │
    │   ├── middleware                # Middleware components for the application.
    │   │   └── client_cache_middleware.py  # Middleware for client-side caching.
    │   │
    │   ├── models                    # SQLModel db and validation models for the application.
    │   │    ├── __init__.py
    │   │    ├── games.py               # SQLModel models for games.
    │   │    ├── rate_limit.py         # SQLModel models for rate limiting.
    │   │    ├── job.py               # SQLModel models for jobs.
    │   │    └── user.py               # SQLModel models for users.
    │   │
    │   └── schemas
    │       ├── __init__.py
    │       ├── games.py             # SQLModel schemas specific to games model.
    │       ├── custom.py            # SQLModel custom schemas.
    │       ├── job.py               # SQLModel schemas for jobs.
    │       ├── opponents.py          # SQLModel schemas for opponents model.
    │       ├── predictions.py        # SQLModel schemas for predictions model.
    │       └── users.py              # SQLModel schemas for user model.
    │    
    ├── migrations                    # Alembic migration scripts for database changes.
    │   ├── README
    │   ├── env.py                    # Environment configuration for Alembic.
    │   ├── script.py.mako            # Template script for Alembic migrations.
    │   │
    │   └── versions                  # Individual migration scripts.
    │
    └── scripts                       # Utility scripts for the application.
        ├── __init__.py
        └── create_first_superuser.py # Script to create the first superuser.
```

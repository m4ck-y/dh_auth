# dh_auth Endpoints Documentation

## Base Path: `/v1/auth`
Protocol: **HTTP/REST**

---

### 1. Login
Authenticates a user and issues JWT tokens via HttpOnly cookies.

- **URL**: `/login`
- **Method**: `POST`
- **Auth Required**: No
- **Request Body**: [LoginRequestDTO](file:///home/m4cky/Documents/dev_me/my_projects/digital_hospital/dh_auth/app/contexts/auth/application/dtos/auth_dto.py)
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **Success Response**: `200 OK`
  - **Body**: `LoginResponseDTO`
  - **Cookies**: 
    - `access_token` (HttpOnly, Secure, Lax)
    - `refresh_token` (HttpOnly, Secure, Lax)

---

### 2. Silent Refresh
Renews the access token using the refresh token stored in cookies. Designed to be called by the API Gateway.

- **URL**: `/refresh`
- **Method**: `POST`
- **Auth Required**: No (Uses `refresh_token` cookie)
- **Success Response**: `200 OK`
  - **Cookies**: 
    - `access_token` (Updated)

---

### 3. Logout
Clears authentication cookies and revokes the session.

- **URL**: `/logout`
- **Method**: `POST`
- **Auth Required**: No
- **Success Response**: `200 OK`
  - **Action**: Deletes `access_token` and `refresh_token` cookies.
### 4. Get Current User (Me)
Returns the profile information of the currently authenticated user, including organizational context and RBAC.

- **URL**: `/me`
- **Method**: `GET`
- **Auth Required**: Yes (Uses `access_token` cookie)
- **Success Response**: `200 OK`
- **Body**: [MeResponseDTO](app/contexts/auth/application/dtos/auth_dto.py)
  ```json
  {
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "first_name": "Juan",
    "last_name": "Pérez",
    "username": "juan.perez",
    "verification_status": "APPROVED",
    "employee": {
      "uuid": "...",
      "status": "ACTIVE",
      "company": {
        "uuid": "...",
        "name": "Hospital Central"
      }
    },
    "tenants": [
      { "uuid": "...", "name": "Sede Norte", "key": "SN01" }
    ],
    "roles": ["ADMIN"],
    "permissions": ["user:create"]
  }
  ```

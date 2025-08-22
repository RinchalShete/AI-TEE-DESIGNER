# AI Tee Designer – Backend

This is the backend service for the AI Tee Designer platform. It handles user authentication, profile management, design generation using Stable Diffusion with LoRA fine-tuning, and image storage in the cloud. The backend is built with FastAPI, Supabase, and integrates with a containerized Stable Diffusion WebUI for AI-based T-shirt designs.

---

## Table of Contents

1. Features
2. Tech Stack
3. Requirements
4. Setup and Installation
5. Environment Variables
6. API Endpoints

---

### Features

- User signup, login, and JWT-based authentication
- Profile management: update username, fetch profile info
- Password recovery via email OTP verification
- Generate front and back T-shirt designs using Stable Diffusion with LoRA
- Compute CLIP similarity score for designs
- Upload generated designs to Cloudinary and store references in Supabase
- Dockerized setup for easy deployment

---

### Tech Stack

- Backend Framework: FastAPI
- Database & Auth: Supabase
- AI Model: Stable Diffusion (v1.5) + LoRA fine-tuned model for T-shirt designs
- Cloud Storage: Cloudinary
- Containerization: Docker & Docker Compose
- Image Evaluation: OpenAI CLIP
- Email Service: SMTP (for OTP)

---

### Requirements

- CPU with 6GB RAM
- Docker and NVIDIA Container Toolkit installed on your system.
- 'stable-diffusion-webui' folder downloaded from Google Drive and placed in the project folder:  https://drive.google.com/drive/folders/1wV1BkFN6GmWByh1-5_-Elagr9cEbWwD3?usp=sharing
- Note: This setup can only be used locally. If you want to make it production-ready, host A1111 with SD v1.5 + LoRA on a GPU server.

---

### Setup & Installation

1. Clone the repository 
```bash
git clone https://github.com/RinchalShete/AI-TEE-DESIGNER.git
cd AI-TEE-DESIGNER
```
2. Set up .env in backend folder ( Example env is given below )
3. Build and run containers
```bash
docker-compose up 
```
4. Backend runs at: http://localhost:8000
5. Stable Diffusion WebUI ( A1111 ) runs at: http://localhost:7860

---

### Environment Variables
| Variable             | Description                        |
|----------------------|------------------------------------|
| CLOUDINARY_CLOUD_NAME | Cloudinary account name            |
| CLOUDINARY_API_KEY    | Cloudinary API key                 |
| CLOUDINARY_API_SECRET | Cloudinary API secret              |
| SUPABASE_URL          | Supabase project URL               |
| SUPABASE_KEY          | Supabase service key               |
| JWT_SECRET            | Secret key for JWT generation      |
| GEMINI_API_KEY        | Optional for AI features           |
| SMTP_SERVER           | Email server for OTP               |
| SMTP_PORT             | SMTP port                          |
| SMTP_EMAIL            | Email account used for sending OTP |
| SMTP_PASSWORD         | Email password                     |
| BLANK_URL             | Placeholder image URL              |

---

### API Endpoints

---

#### Auth

| Method | Endpoint   | Description                       |
|--------|------------|-----------------------------------|
| POST   | /auth/signup | Create a new user & auto-login   |
| POST   | /auth/login  | Login and return JWT             |
| GET    | /auth/me     | Get current logged-in user info  |

---

#### Profile

| Method | Endpoint                   | Description                       |
| ------ | -------------------------- | --------------------------------- |
| GET    | /profile/                | Get user profile + designs        |
| PUT    | /profile/update          | Update user profile info          |
| POST   | /profile/forgot-password | Send OTP for password reset       |
| POST   | /profile/verify-otp      | Verify OTP                        |
| POST   | /profile/reset-password  | Reset password using verified OTP |

---

#### Designs

| Method | Endpoint           | Description                                                           |
| ------ | ------------------ | --------------------------------------------------------------------- |
| POST   | /generate-design | Generate front/back T-shirt design, compute CLIP score, and save URLs |



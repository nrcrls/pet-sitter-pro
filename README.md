# Pet Sitter Pro

Pet Sitter Pro is a web application designed to help pet sitters manage their pet sitting schedules and client information.
This project was born out of my experience as a pet sitter and also as a way for me to learn Django.

## Features

- **User Authentication**: Secure registration and login for pet owners and sitters.
- **Profile Management**: Create and update pet profiles with personal details and pet information.
- **Booking System**: Schedule and manage pet sitting appointments.
- **Responsive Design**: Optimised for both desktop and mobile devices.

Next Steps:
- **Income Data**: Visualise income earned with graphs.
- **Django Rest Framework**: Use DRF to create API and integrate it with a frontend framework.

## Technologies Used

- **Backend**: Python, Django
- **Frontend**: Tailwind CSS, DaisyUI
- **Database**: Postgres
- **Containerization**: Docker

## Getting Started

Follow these steps to set up the project locally.

### Prerequisites

- Docker
- Docker Compose

### Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/nrcrls/pet-sitter-pro.git
   cd pet-sitter-pro

2. **Build and run the Docker containers:
    ```docker-compose up --build -d

3. **Apply database migrations:
    ```docker-compose exec web python manage.py migrate

4. **Create a superuser (optional):
    ```docker-compose exec web python manage.py createsuperuser

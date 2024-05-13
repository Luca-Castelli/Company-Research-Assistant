# Company Research Tool

## Overview

This web-based application generates detailed reports about companies using Dockerized services including a Streamlit web interface, a backend Python application, and Redis for caching.

## Features

- **Comprehensive Reports**: Summarizes company overview, business model, financials, and more.
- **Caching**: Uses Redis to improve response times and reduce load.
- **Interactive Web Interface**: Powered by Streamlit for easy usage.

## Prerequisites

- Docker and Docker Compose
- Python (for non-Docker components)

## Quick Start

1. **Clone and navigate to repo**
   ```bash
   git clone https://github.com/yourusername/company-research-tool.git
   cd company-research-tool
   ```
2. **Run Docker Compose**
   ```bash
   docker-compose up --build
   ```

## Usage

Access the web interface at http://localhost:8501. Enter in a company website URL and click "Analyze" to generate the report.

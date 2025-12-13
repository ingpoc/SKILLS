#!/bin/bash
# Environment initialization script for PROJECT_NAME
# Generated on $(date)

set -e  # Exit on any error

echo "🚀 Initializing PROJECT_NAME environment..."

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if required tools are installed
check_requirements() {
    echo "Checking requirements..."

    # Add your project-specific requirements here
    # Example:
    # command -v node >/dev/null 2>&1 || { print_error "Node.js is required but not installed."; exit 1; }
    # command -v python3 >/dev/null 2>&1 || { print_error "Python 3 is required but not installed."; exit 1; }

    print_status "All requirements met"
}

# Install dependencies
install_dependencies() {
    echo "Installing dependencies..."

    # Node.js project
    if [ -f "package.json" ]; then
        print_status "Installing Node.js dependencies..."
        npm install
    fi

    # Python project
    if [ -f "requirements.txt" ]; then
        print_status "Installing Python dependencies..."
        pip install -r requirements.txt
    fi

    if [ -f "requirements.dev.txt" ]; then
        print_status "Installing Python dev dependencies..."
        pip install -r requirements.dev.txt
    fi

    # Ruby project
    if [ -f "Gemfile" ]; then
        print_status "Installing Ruby gems..."
        bundle install
    fi

    # Rust project
    if [ -f "Cargo.toml" ]; then
        print_status "Building Rust project..."
        cargo build
    fi
}

# Setup database
setup_database() {
    if [ -d "database" ] || [ -f "schema.sql" ] || grep -q "DATABASE_URL" .env.example 2>/dev/null; then
        echo "Setting up database..."

        # Add your database setup here
        # Example:
        # if command -v psql >/dev/null 2>&1; then
        #     createdb project_name || print_warning "Database might already exist"
        #     psql -d project_name -f schema.sql || print_error "Database setup failed"
        # fi

        print_status "Database setup complete"
    fi
}

# Create environment files
setup_environment() {
    echo "Setting up environment..."

    # Create .env from template
    if [ -f ".env.example" ] && [ ! -f ".env" ]; then
        cp .env.example .env
        print_status "Created .env from template"
        print_warning "Please update .env with your configuration"
    fi

    # Create required directories
    mkdir -p logs
    mkdir -p temp
    mkdir -p uploads
    print_status "Created required directories"
}

# Build the project
build_project() {
    echo "Building project..."

    # Add your build commands here
    # Example:
    # npm run build
    # cargo build --release
    # make build

    print_status "Build complete"
}

# Run tests
run_tests() {
    if [ -f "package.json" ] && npm run test --silent 2>/dev/null; then
        echo "Running tests..."
        npm test
        print_status "All tests passed"
    elif [ -f "pytest.ini" ] || [ -f "setup.cfg" ] && grep -q "pytest" setup.cfg 2>/dev/null; then
        echo "Running tests..."
        pytest
        print_status "All tests passed"
    else
        print_warning "No test configuration found"
    fi
}

# Start development server
start_dev_server() {
    echo "Starting development server..."

    # Add your dev server command here
    # Example:
    # npm run dev
    # python -m src.server
    # cargo run

    print_status "Development server started"
}

# Main execution
main() {
    echo ""
    echo "=================================="
    echo "  PROJECT_NAME Setup Script"
    echo "=================================="
    echo ""

    check_requirements
    setup_environment
    install_dependencies
    setup_database
    build_project
    run_tests

    echo ""
    echo "✅ Setup complete!"
    echo ""
    echo "Next steps:"
    echo "1. Review and update .env file"
    echo "2. Start development with: $0 dev"
    echo ""
}

# Handle command line arguments
case "$1" in
    "dev"|"start")
        start_dev_server
        ;;
    "test")
        run_tests
        ;;
    "build")
        build_project
        ;;
    *)
        main
        ;;
esac
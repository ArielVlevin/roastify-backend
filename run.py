
import argparse
import os
import sys

def main():
    """Parse arguments and start the application."""
    parser = argparse.ArgumentParser(description="Coffee Roaster API")
    parser.add_argument('--port', type=int, default=8000, help='Port number')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host address')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload')
    parser.add_argument('--simulation', action='store_true', help='Run in simulation mode')
    parser.add_argument('--hardware', action='store_true', help='Run with hardware support')
    
    args = parser.parse_args()
    
    # Set environment variables based on args
    os.environ['HOST'] = args.host
    os.environ['PORT'] = str(args.port)
    os.environ['DEBUG'] = '1' if args.debug else '0'
    
    # Determine mode (default to simulation if not specified)
    if args.hardware:
        os.environ['SIMULATION_MODE'] = '0'
        print("Starting in hardware mode with Phidget support")
    else:
        os.environ['SIMULATION_MODE'] = '1'
        print("Starting in simulation mode (no hardware required)")
    
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"Debug mode: {'Enabled' if args.debug else 'Disabled'}")
    print(f"Auto-reload: {'Enabled' if args.reload else 'Disabled'}")
    
    # Import and start the application
    try:
        from app import start
        start()
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
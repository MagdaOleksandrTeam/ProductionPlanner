from models.database import init_db

def main():
    
    init_db()
    
    print("Production Planner started!")

if __name__ == "__main__":
    main()

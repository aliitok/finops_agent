from services.analysis import explain
import json

def main():
    account_id = input("Enter account_id: ")
    result = explain(account_id)

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
"Little script to add new users to the algorithm"
import json

def main():
    input_file = open("users.json", "r")
    existing_users = json.load(input_file)
    input_file.close()
    while True:
        twitter_handle = input("Twitter handle : @")
        if twitter_handle == "":
            break
        banned_words = input("Banned words, space separated : ").split(" ")
        existing_users.append({
            "name": twitter_handle,
            "banned_words": banned_words})
    print("Saving users")
    output_file = open("users.json", "w")
    json.dump(existing_users, output_file)
    output_file.close()


if __name__ == "__main__":
    main()

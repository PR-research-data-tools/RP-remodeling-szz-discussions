import json
import dateparser


def main():
    with open('extended_normal_dataset.json', 'r') as json_file:
        my_list = json.load(json_file)
    json_file.close()

    item = my_list[0]
    date = dateparser.parse(item['earliest_issue_date'])
    print(date)


if __name__ == "__main__":
    main()
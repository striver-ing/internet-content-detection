import sys
sys.path.append('..')
import utils.tools as tools

def main():
    contents = tools.read_file('to_json.txt', readlines = True)

    json = {}
    for content in contents:
        if content == '\n':
            continue

        content = content.strip()
        regex = ['(.*?):(.*)', '(.*?):? +(.*)', '([^:]*)']

        result = tools.get_info(content, regex)
        result = result[0] if isinstance(result[0], tuple) else result
        json[result[0]] = result[1]

    print(tools.dumps_json(json))



if __name__ == '__main__':
    main()

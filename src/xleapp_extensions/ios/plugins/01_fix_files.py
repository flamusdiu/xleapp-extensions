import pathlib
import re

regex_non_category = re.compile(r"class [\w]+\((?<!category)\w+\)")
regex_artifact = re.compile(r"^(class [\w]+)\((?<!category)\w+\):$")
regex_name = re.compile(r'self.name = "([\w &()-]+)"')
regex_category = re.compile(r'self.category = "([\w &()-]+)"')


def folder():
    return pathlib.Path(__file__).parent


def main():
    for it in folder().glob("*.py"):
        if it.suffix == ".py" and it.stem not in ["__init__", __file__]:
            with open(it, mode="r+") as plugin:
                plugin_file = plugin.read()
                plugin.seek(0)
                plugin_file_list = plugin.readlines()

                if regex_non_category.search(plugin_file):
                    artifact, label, category = None, None, None
                    for line_num, line in enumerate(plugin_file_list):

                        if regex_artifact.search(line):
                            artifact = line_num

                        if regex_name.search(line):
                            label = (line_num, regex_name.search(line).group(1))

                        if regex_category.search(line):
                            category = (line_num, regex_category.search(line).group(1))

                    plugin_file_list[artifact] = re.sub(
                        regex_artifact,
                        f'\\1(Artifact, category = "{category[1]}", label = "{label[1]}"):',
                        plugin_file_list[artifact],
                    )

                    plugin_file_list.pop(label[0])
                    plugin_file_list.pop(category[0])

                    plugin.seek(0)
                    plugin.writelines(plugin_file_list)
                    plugin.truncate()


if __name__ == "__main__":
    main()

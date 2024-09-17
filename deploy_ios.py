import pandas as pd
import os
import shutil
import re
import yaml


def replace_text_in_yaml(filename, old_text, new_text):
    try:
        with open(filename, "r") as f:
            data = yaml.safe_load(f)

        def replace_text_recursive(data):
            if isinstance(data, str):
                return data.replace(old_text, new_text)
            elif isinstance(data, list):
                return [replace_text_recursive(item) for item in data]
            elif isinstance(data, dict):
                return {replace_text_recursive(key): replace_text_recursive(value) for key, value in data.items()}
            else:
                return data

        modified_data = replace_text_recursive(data)

        with open(filename, "w") as f:
            yaml.dump(modified_data, f, default_flow_style=False)

        print(f"Replaced '{old_text}' with '{new_text}' in '{filename}'.")
    except (IOError, yaml.YAMLError) as e:
        print(f"Error replacing text: {e}")


def get_app_name(dart_file):
    with open(dart_file, 'r') as f:
        content = f.read()
        match = re.search(r"appTitle = '(.*?)'", content)
        if match:
            return match.group(1)
        else:
            return 'unknown_app'


def build_and_deploy(dart_file_path):
    app_name = get_app_name(dart_file_path)
    print("--------------------------------------------------")
    print("starting for the app " + app_name)

    initial_version = "1.0.0+1"
    current_version = int(versionList[i])
    new_version = f"{current_version + 1}.0.0+1"

    filename = "pubspec.yaml"
    replace_text_in_yaml(filename, 'images/kamero', f'images/{appNameList[i]}')
    replace_text_in_yaml(filename, initial_version, new_version)

    os.system("flutter pub get")

    build_command = f"flutter build ipa --flavor {appNameList[i]} -t {dart_file_path}"
    os.system(build_command)
    print("build completed")

    source_path = f"{script_dir}/build/ios/ipa/kamero.ipa"
    destination_path = f"{script_dir}/ipa_files/{appNameList[i]}.ipa"

    try:
        shutil.copy2(source_path, destination_path)
        print(f"File copied and renamed successfully: {destination_path}")
    except shutil.Error as err:
        print(f"Error copying file: {err}")

    filename = "pubspec.yaml"
    replace_text_in_yaml(filename, f'images/{appNameList[i]}',  'images/kamero')
    replace_text_in_yaml(filename, new_version, initial_version)

    print("----------------------")
    print("xcode upload started")
    xcode_upload_command = (f"xcrun altool --upload-app --type ios -f "
                            f"{destination_path} --apiKey "
                            f"{apiKeyList[i]} --apiIssuer {issuerIdList[i]}")

    os.system(xcode_upload_command)
    print(xcode_upload_command)
    print("xcode upload completed")
    print("-----------------------")
    print("completed successfully for the app " + app_name)


if __name__ == "__main__":

    os.makedirs("ipa_files", exist_ok=True)

    dataframe = pd.read_excel('key_sheet.xlsx')
    whiteLabelList = dataframe['whiteLabel']
    appNameList = dataframe['appName']
    apiKeyList = dataframe['apiKey']
    issuerIdList = dataframe['issuerId']
    versionList = dataframe['currentVersion']

    script_dir = os.path.dirname(__file__)
    print(script_dir)

    for i in range(len(whiteLabelList)):
        dartFilePath = f"{script_dir}/lib/whitelabel/main_{whiteLabelList[i]}.dart"
        build_and_deploy(dartFilePath)

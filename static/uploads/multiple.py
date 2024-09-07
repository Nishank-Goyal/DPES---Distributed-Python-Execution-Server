# Define the content you want to write to the file
file_content = """This is a sample text file.
It contains multiple lines of text.
You can customize this content as needed.
"""

# Specify the file name
file_name = "output.txt"

# Open the file in write mode and write the content
with open(file_name, "w") as file:
    file.write(file_content)

print(f"File '{file_name}' has been created with the desired content.")

from pathlib import Path


def write_lines(filename):
    with open(filename, "w") as f:
        for i in range(5):
            line = f"Printing {i}"
            f.write(line)
            print(line)


print("Starting!")

output_file = "output.txt"
if Path(output_file).exists():
    print(f"Already wrote to {output_file}!")
else:
    write_lines(output_file)

print("Bye!")

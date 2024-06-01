import matplotlib.pyplot as plt

def count_digits(filename):
    try:
        with open(filename, 'r') as file:
            text = file.read()

        count_0 = text.count('0')
        count_1 = text.count('1')
        count_2 = text.count('2')

        total = count_0 + count_1 + count_2
        count_0 = (count_0 / total)
        count_1 = (count_1 / total)
        count_2 = (count_2 / total)
        print(total)
        return count_0, count_1, count_2
    except FileNotFoundError:
        return "The file was not found."


filename = input("Enter the name of the file: ")
count_0, count_1, count_2 = count_digits(filename)

print(f"Number of 0s: {count_0}")
print(f"Number of 1s: {count_1}")
print(f"Number of 2s: {count_2}")

counts = count_digits(filename)

if isinstance(counts, str):
    print(counts)
else:
    count_0, count_1, count_2 = counts

    # Data for plotting
    digits = ['0', '1', '2']
    values = [count_0, count_1, count_2]

    # Plotting the bar chart
    plt.bar(digits, values, color=['blue', 'orange', 'green'])
    plt.xlabel('Agents')
    plt.ylabel('Win Percentage')
    plt.title('Win Percentage of Agents')
    plt.show()

    # Print counts
    print(f"Number of 0s: {count_0}")
    print(f"Number of 1s: {count_1}")
    print(f"Number of 2s: {count_2}")

import matplotlib.pyplot as plt

human_data = [
    [('Settlement', (4, 6)), ('City', (4, 2)), ('City', (4, 2)), ('City', (2, 5)), ('Settlement', (4, 6)), ('Settlement', (4, 6)), ('City', (4, 2)), 
     ('City', (4, 2)), ('City', (4, 2)), ('City', (4, 2)), ('City', (4, 2)), ('City', (4, 2)), ('Settlement', (6, 3))], 
     [('Settlement', (2, 5)), ('Settlement', (2, 5)), ('City', (4, 6)), ('City', (4, 6)), ('Settlement', (2, 5)), ('Settlement', (6, 5)), 
      ('City', (2, 3)), ('Settlement', (6, 5)), ('City', (4, 6)), ('City', (4, 6)), ('City', (4, 6)), ('City', (4, 6)), ('City', (4, 6))], 
      [('Settlement', (4, 2)), ('City', (2, 5)), ('Settlement', (4, 2)), ('Settlement', (4, 6)), ('City', (4, 4)), ('Settlement', (4, 2)), 
       ('City', (4, 4)), ('City', (4, 4)), ('City', (4, 4)), ('Settlement', (4, 6)), ('Settlement', (4, 6)), ('Settlement', (4, 2)), ('City', (2, 5))], 
       [('City', (4, 2)), ('Settlement', (4, 6)), ('City', (4, 2)), ('City', (4, 2)), ('Settlement', (4, 6)), ('City', (4, 2)), ('Settlement', (4, 6)),
         ('Settlement', (4, 6)), ('Settlement', (4, 6)), ('City', (4, 2)), ('City', (4, 2)), ('City', (4, 2)), ('City', (4, 2))], 
         [('City', (2, 5)), ('City', (2, 5)), ('Settlement', (4, 2)), ('City', (2, 5)), ('City', (2, 5)), ('City', (2, 5)), ('City', (2, 5)), 
          ('City', (2, 5)), ('City', (2, 5)), ('City', (2, 5)), ('City', (4, 4)), ('Settlement', (4, 2)), ('City', (4, 6))]]

human_data_posterior_raw = {}
for i, exp in enumerate(human_data):
    human_data_posterior_raw[i] = {}
    for answer in exp:
        if answer not in human_data_posterior_raw[i]:
            human_data_posterior_raw[i][answer] = 0
        human_data_posterior_raw[i][answer] += 1

print(human_data_posterior_raw)


for exp, raw_data in human_data_posterior_raw.items():
    freqs = {hypothesis: value/13 for hypothesis, value in raw_data.items()}
    x_values = list(str(f) for f in freqs.keys())
    y_values= list(freqs.values())

    # Create the bar graph
    plt.figure(figsize=(8, 5))  # Optional: Adjust figure size
    plt.bar(x_values, y_values, color='skyblue', edgecolor='black')

    # Add labels and title
    plt.xlabel('Hypotheses')
    plt.ylabel('Response Distributions')
    plt.title('Human Data')
    plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for better readability

    # Display the graph
    plt.tight_layout()
    plt.show()





import pickle 
import os
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats

def analyze_data(exps):
    '''
    Shows posterior data, calculates chi-square, and imports pdb for further analysis
    exps: list of ints, indicating which experiments to analyze
    '''
    human_posterior_data = {
        1: {('settlement', (4, 6)): 0.23076923076923078, ('city', (4, 2)): 0.6153846153846154, ('city', (2, 5)): 0.07692307692307693, ('settlement', (6, 3)): 0.07692307692307693}, 
        2: {('settlement', (2, 5)): 0.23076923076923078, ('city', (4, 6)): 0.5384615384615384, ('settlement', (6, 5)): 0.15384615384615385, ('city', (2, 3)): 0.07692307692307693}, 
        3: {('settlement', (4, 2)): 0.3076923076923077, ('city', (2, 5)): 0.15384615384615385, ('settlement', (4, 6)): 0.23076923076923078, ('city', (4, 4)): 0.3076923076923077}, 
        4: {('city', (4, 2)): 0.6153846153846154, ('settlement', (4, 6)): 0.38461538461538464}, 
        5: {('city', (2, 5)): 0.6923076923076923, ('settlement', (4, 2)): 0.15384615384615385, ('city', (4, 4)): 0.07692307692307693, ('city', (4, 6)): 0.07692307692307693}
    }

    # Number of human subjects
    N_humans = 13

    for num in exps:
        vp_path = r'C:\Users\ljdde\Downloads\9.66\Catan_Final_Project\data\newsm_raw_experiment_data\experiment_0{num}_raw_vp_data.pkl'


        with open(vp_path, 'rb') as file:
            vp_freqs = pickle.load(file)
            sort_dem = sorted(vp_freqs.items(), key=lambda x: vp_freqs[x[0]], reverse=True)

        num_samples = sum(vp_freqs.values())
        vp_posteriors = {vp: freq/num_samples for vp, freq in sort_dem}

        # Align human data with model keys
        human_posteriors = {}
        for hypothesis in vp_posteriors.keys():
            if hypothesis in human_posterior_data[num]:
                human_posteriors[hypothesis] = human_posterior_data[num][hypothesis]
            else:
                human_posteriors[hypothesis] = 0

        # Convert keys to strings for plotting
        x_values = list(str(k) for k in vp_posteriors.keys())
        y_values_model = list(vp_posteriors.values())
        y_values_human = list(human_posteriors.values())

        # Calculate chi-square
        # Convert probabilities to counts
        observed = [p * N_humans for p in y_values_human]
        expected = [p * N_humans for p in y_values_model]

        # Normalize expected counts to match the sum of observed counts
        sum_observed = sum(observed)
        sum_expected = sum(expected)

        if sum_expected != 0:
            expected = [val * (sum_observed / sum_expected) for val in expected]

        chi2, p_value = stats.chisquare(f_obs=observed, f_exp=expected)
        print(f"Experiment {num}: Chi2 = {chi2:.4f}, p-value = {p_value:.4f}")

        # Width of each bar
        bar_width = 0.35

        # Create numerical positions for each category
        x_positions = np.arange(len(x_values))

        # Plot the first set of bars (Model)
        plt.bar(x_positions, y_values_model, width=bar_width, color='skyblue', edgecolor='black', label='Model')

        # Plot the second set of bars (Human), shifted by the bar width
        plt.bar(x_positions + bar_width, y_values_human, width=bar_width, color='lightgreen', edgecolor='black', label='Human')

        # Add labels and title
        plt.xlabel('Hypotheses')
        plt.ylabel('Posterior Probability')
        plt.title(f'Posterior Distribution (Model vs. Human) - Experiment {num}')

        # Adjust the x-axis ticks to be between the groups of bars
        plt.xticks(x_positions + bar_width/2, x_values, rotation=45, ha='right')

        plt.legend()
        plt.tight_layout()
        plt.show()

        #import pdb; pdb.set_trace()


analyze_data([1,2,3,4,5])
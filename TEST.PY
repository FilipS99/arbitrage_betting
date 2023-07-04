import itertools


def generate_word_combinations(sentence):
    words = sentence.split()
    unique_words = set(words)
    combinations = []

    # Generate permutations of all unique words
    for permutation in itertools.permutations(unique_words):
        combination = ' '.join(permutation)
        combinations.append(combination)

        # Generate combinations with abbreviations
        for i in range(len(permutation)):
            abbreviation = permutation[i][0] + '.'
            abbreviated_permutation = permutation[:i] + \
                (abbreviation,) + permutation[i+1:]
            abbreviated_combination = ' '.join(abbreviated_permutation)

            # Check if abbreviation contains duplicate words
            if len(set(abbreviated_permutation)) == len(abbreviated_permutation) and not any(word.startswith(abbreviation) for word in permutation[i+1:]):
                combinations.append(abbreviated_combination)

            # Generate combinations with multiple abbreviations
            for j in range(i + 2, len(permutation) + 1):
                multi_abbreviations = [
                    word[0] + '.' for word in permutation[i:j]]
                multi_abbreviations_permutation = permutation[:i] + tuple(
                    multi_abbreviations) + permutation[j:]
                multi_abbreviations_combination = ' '.join(
                    multi_abbreviations_permutation)

                # Check if multi-abbreviations contain duplicate words
                if len(set(multi_abbreviations_permutation)) == len(multi_abbreviations_permutation) and not any(word.startswith(multi_abbreviations[0]) for word in permutation[i+1:j]):
                    combinations.append(multi_abbreviations_combination)

    return combinations


# Example usage
sentence = "Iga Świątek"
combinations = set(generate_word_combinations(sentence))
longest_combination = max(combinations)
for combination in combinations:
    print("'"+combination+"': '"+longest_combination+"'")

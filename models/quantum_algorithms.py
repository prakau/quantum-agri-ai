"""
This module implements Grover's algorithm, a quantum algorithm for searching an
unsorted database or finding a specific item in a set of items.

Grover's algorithm provides a quadratic speedup over classical search algorithms
for unsorted data. For a database of N items, a classical search would take O(N)
evaluations on average, while Grover's algorithm takes O(sqrt(N)) evaluations.

How it works:
1.  Initialization: Start with a quantum register of n qubits, where N = 2^n is
    the total number of items in the search space. Initialize the qubits in an
    equal superposition of all possible states. This means each of the N states
    has an equal probability of being measured.
2.  Oracle: Apply an "oracle" operator. The oracle is a black box function that
    identifies the desired item(s). It "marks" the target state(s) by negating
    their amplitude. All other states are left unchanged.
3.  Amplification (Diffuser): Apply a "diffusion" operator (also known as
    Grover's diffusion operator or inversion about the mean). This operation
    amplifies the amplitudes of the marked states and reduces the amplitudes of
    the unmarked states. It essentially reflects all amplitudes about the mean
    amplitude.
4.  Iteration: Repeat steps 2 and 3 for a specific number of times, approximately
    sqrt(N) times. Each iteration further increases the amplitude of the marked
    state(s).
5.  Measurement: After the iterations, measure the quantum state. The probability
    of measuring the marked state will be very high.

The key components are the oracle, which knows how to identify the item, and the
diffusion operator, which amplifies its probability.
"""

import numpy as np

class Grover:
    """
    Implements Grover's search algorithm.

    The algorithm operates on a state vector representing the amplitudes of quantum states.
    It iteratively applies an oracle and a diffusion operator to amplify the
    amplitude of the target state(s).
    """

    def __init__(self, num_qubits, oracle_function):
        """
        Initializes Grover's algorithm.

        Args:
            num_qubits (int): The number of qubits to use. The search space will
                              have 2^num_qubits items.
            oracle_function (callable): A function that takes an integer representing
                                       a computational basis state index and returns
                                       True if it's a marked item, False otherwise.
                                       For example, if num_qubits is 3, state_index 5
                                       corresponds to the state |101>.
        """
        if not isinstance(num_qubits, int) or num_qubits <= 0:
            raise ValueError("Number of qubits must be a positive integer.")
        self.num_qubits = num_qubits
        self.num_states = 2**self.num_qubits

        if not callable(oracle_function):
            raise TypeError("oracle_function must be a callable function.")
        self.oracle_function = oracle_function

        self.state_vector = self._initial_state()
        print(f"Grover algorithm initialized for {self.num_qubits} qubits ({self.num_states} states).")

    def _initial_state(self):
        """
        Creates the initial uniform superposition of all possible basis states.
        Each state |x> has an amplitude of 1/sqrt(N).

        Returns:
            numpy.ndarray: A complex vector representing the initial state.
        """
        print("Creating initial superposition...")
        amplitude = 1 / np.sqrt(self.num_states)
        initial_state = np.full(self.num_states, amplitude, dtype=complex)
        # print(f"Initial state vector: {initial_state}")
        return initial_state

    def _oracle(self):
        """
        Applies the oracle operator to the current state vector.
        The oracle marks the desired item(s) by negating their amplitude(s).
        U_omega |x> = -|x> if x is the target state
        U_omega |x> =  |x> if x is not the target state
        """
        print("Applying oracle...")
        for i in range(self.num_states):
            # The oracle_function checks if the state corresponding to index 'i' is the marked one.
            if self.oracle_function(i):
                # print(f"  Marking state {i} (binary: |{i:0{self.num_qubits}b}>)")
                self.state_vector[i] = -self.state_vector[i]
        # print(f"State vector after oracle: {self.state_vector}")

    def _diffuser(self):
        """
        Applies the Grover diffusion operator (inversion about the mean).
        This operator amplifies the amplitudes of the marked states.
        The operation is D = 2|s><s| - I, where |s> is the uniform superposition
        and I is the identity matrix.
        Effectively, for each amplitude A_i, it transforms it to 2*mean - A_i.
        """
        print("Applying diffuser (inversion about the mean)...")
        # 1. Calculate the mean amplitude
        mean_amplitude = np.mean(self.state_vector)
        # print(f"  Mean amplitude: {mean_amplitude}")

        # 2. Invert about the mean: Psi_new = 2 * mean - Psi_old
        self.state_vector = 2 * mean_amplitude - self.state_vector
        # print(f"State vector after diffuser: {self.state_vector}")

    def run_algorithm(self, num_iterations=None):
        """
        Runs Grover's algorithm for a specified number of iterations.

        Args:
            num_iterations (int, optional): The number of iterations to perform.
                                            If None, it defaults to the optimal
                                            number, floor(pi/4 * sqrt(N)).

        Returns:
            int: The index of the measured state (the one with the highest
                 probability after the iterations). This corresponds to the
                 computational basis state that is most likely the target.
        """
        if num_iterations is None:
            # Optimal number of iterations
            num_iterations = int(np.floor(np.pi / 4 * np.sqrt(self.num_states)))
            print(f"Optimal number of iterations chosen: {num_iterations}")
        elif not isinstance(num_iterations, int) or num_iterations < 0:
            raise ValueError("Number of iterations must be a non-negative integer.")

        if num_iterations == 0:
            print("Warning: Running with 0 iterations. Measurement will be on the initial state.")
        
        print(f"Running Grover's algorithm for {num_iterations} iterations...")

        for iteration in range(num_iterations):
            print(f"  Iteration {iteration + 1}/{num_iterations}:")
            # print(f"    State before oracle: {np.round(self.state_vector, 3)}")
            self._oracle()
            # print(f"    State after oracle: {np.round(self.state_vector, 3)}")
            self._diffuser()
            # print(f"    State after diffuser: {np.round(self.state_vector, 3)}")
            # print(f"    Current probabilities: {np.round(self.get_probabilities(), 3)}")


        # Measurement: Find the state with the highest probability
        probabilities = self.get_probabilities()
        # print(f"  Final probabilities after {num_iterations} iterations: {np.round(probabilities, 3)}")
        
        measured_state_index = np.argmax(probabilities)
        print(f"Measurement: Most probable state index is {measured_state_index} with probability {probabilities[measured_state_index]:.4f}")
        return measured_state_index

    def get_probabilities(self):
        """
        Calculates the probabilities of measuring each computational basis state.
        The probability of a state |x> is |amplitude_x|^2.

        Returns:
            numpy.ndarray: An array of probabilities for each state.
        """
        return np.abs(self.state_vector)**2

def example_oracle_factory(marked_item_index, num_total_items):
    """
    Factory function to create a simple oracle.
    The oracle marks a specific computational basis state index.

    Args:
        marked_item_index (int): The index of the item to be marked.
                                 Must be between 0 and num_total_items - 1.
        num_total_items (int): The total number of items in the search space (2^num_qubits).

    Returns:
        callable: An oracle function that takes a state index and returns True
                  if it's the marked_item_index, False otherwise.
    
    Raises:
        ValueError: If marked_item_index is out of bounds.
    """
    if not (0 <= marked_item_index < num_total_items):
        raise ValueError(f"marked_item_index {marked_item_index} is out of bounds for {num_total_items} items.")

    def oracle(current_state_index):
        """Checks if current_state_index is the one to be marked."""
        return current_state_index == marked_item_index
    return oracle

if __name__ == '__main__':
    # --- Example Usage ---
    N_QUBITS = 4  # Number of qubits
    # The item we are searching for (e.g., its index in the database)
    # For N_QUBITS = 4, states are 0 to 15. Let's search for 13 (|1101>)
    MARKED_ITEM_INDEX = 13

    print("="*50)
    print(f"Grover's Algorithm Example: Searching for item {MARKED_ITEM_INDEX}")
    print(f"Number of qubits: {N_QUBITS} (Search space size: {2**N_QUBITS})")
    print("="*50)

    # 1. Create the oracle function
    # The oracle "knows" which item is the correct one.
    oracle_for_item_13 = example_oracle_factory(
        marked_item_index=MARKED_ITEM_INDEX,
        num_total_items=2**N_QUBITS
    )

    # 2. Initialize Grover's algorithm
    grover_search = Grover(num_qubits=N_QUBITS, oracle_function=oracle_for_item_13)

    # Print initial state probabilities (should be uniform)
    initial_probs = grover_search.get_probabilities()
    print(f"\nInitial state probabilities (first 5): {np.round(initial_probs[:5], 4)}")
    print(f"Probability of marked item ({MARKED_ITEM_INDEX}) initially: {initial_probs[MARKED_ITEM_INDEX]:.4f}")

    # 3. Run the algorithm
    # The optimal number of iterations is approx. (pi/4)*sqrt(N)
    # For N_QUBITS=4, N=16, sqrt(N)=4. Iterations = floor(pi/4 * 4) = floor(pi) = 3
    # Let the algorithm determine the optimal number of iterations.
    measured_index = grover_search.run_algorithm()

    # 4. Results
    print("\n" + "="*50)
    print("Algorithm Finished")
    print("="*50)
    print(f"Measured state index: {measured_index}")
    print(f"Binary representation of measured state: |{measured_index:0{N_QUBITS}b}>")

    final_probabilities = grover_search.get_probabilities()

    if measured_index == MARKED_ITEM_INDEX:
        print(f"\nSUCCESS! Found the marked item ({MARKED_ITEM_INDEX}).")
    else:
        print(f"\nFAILURE. Did not find the marked item. Found {measured_index} instead.")
        print("This can happen if the number of iterations is not optimal, or due to the probabilistic nature.")

    print(f"\nProbability of marked item ({MARKED_ITEM_INDEX}) after iterations: {final_probabilities[MARKED_ITEM_INDEX]:.4f}")
    print(f"Probability of measured item ({measured_index}) after iterations: {final_probabilities[measured_index]:.4f}")

    # print("\nFinal probabilities for all states:")
    # for i, prob in enumerate(final_probabilities):
    #     print(f"  State |{i:0{N_QUBITS}b}> (Index {i}): Probability = {prob:.4f} {'<-- MARKED' if i == MARKED_ITEM_INDEX else ''} {'<-- MEASURED' if i == measured_index else ''}")

    # --- Example with a different marked item and explicit iterations ---
    N_QUBITS_2 = 3
    MARKED_ITEM_INDEX_2 = 2 # Search for |010>
    NUM_ITERATIONS_2 = 1 # For N=8, optimal is floor(pi/4 * sqrt(8)) = floor(pi/4 * 2.82) = floor(2.21) = 2. Let's try 1.

    print("\n" + "="*50)
    print(f"Second Example: Searching for item {MARKED_ITEM_INDEX_2} ({N_QUBITS_2} qubits)")
    print(f"Explicitly setting {NUM_ITERATIONS_2} iteration(s).")
    print("="*50)

    oracle_for_item_2 = example_oracle_factory(
        marked_item_index=MARKED_ITEM_INDEX_2,
        num_total_items=2**N_QUBITS_2
    )
    grover_search_2 = Grover(num_qubits=N_QUBITS_2, oracle_function=oracle_for_item_2)
    measured_index_2 = grover_search_2.run_algorithm(num_iterations=NUM_ITERATIONS_2)
    
    print("\n" + "="*50)
    print("Second Algorithm Finished")
    print("="*50)
    print(f"Measured state index: {measured_index_2}")
    print(f"Binary representation: |{measured_index_2:0{N_QUBITS_2}b}>")
    final_probabilities_2 = grover_search_2.get_probabilities()

    if measured_index_2 == MARKED_ITEM_INDEX_2:
        print(f"\nSUCCESS! Found the marked item ({MARKED_ITEM_INDEX_2}).")
    else:
        print(f"\nFAILURE. Did not find the marked item. Found {measured_index_2} instead.")

    print(f"Probability of marked item ({MARKED_ITEM_INDEX_2}) after {NUM_ITERATIONS_2} iteration(s): {final_probabilities_2[MARKED_ITEM_INDEX_2]:.4f}")

    # Optimal iterations for N_QUBITS_2 = 3 (N=8) is 2. Let's try that.
    NUM_ITERATIONS_3 = 2
    print("\n" + "="*50)
    print(f"Third Example: Searching for item {MARKED_ITEM_INDEX_2} ({N_QUBITS_2} qubits)")
    print(f"Explicitly setting {NUM_ITERATIONS_3} iteration(s) (optimal for N=8).")
    print("="*50)
    grover_search_3 = Grover(num_qubits=N_QUBITS_2, oracle_function=oracle_for_item_2) # Re-initialize
    measured_index_3 = grover_search_3.run_algorithm(num_iterations=NUM_ITERATIONS_3)
    print("\n" + "="*50)
    print("Third Algorithm Finished")
    print("="*50)
    print(f"Measured state index: {measured_index_3}")
    print(f"Binary representation: |{measured_index_3:0{N_QUBITS_2}b}>")
    final_probabilities_3 = grover_search_3.get_probabilities()
    if measured_index_3 == MARKED_ITEM_INDEX_2:
        print(f"\nSUCCESS! Found the marked item ({MARKED_ITEM_INDEX_2}).")
    else:
        print(f"\nFAILURE. Did not find the marked item. Found {measured_index_3} instead.")
    print(f"Probability of marked item ({MARKED_ITEM_INDEX_2}) after {NUM_ITERATIONS_3} iteration(s): {final_probabilities_3[MARKED_ITEM_INDEX_2]:.4f}")

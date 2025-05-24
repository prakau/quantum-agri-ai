import unittest
import numpy as np
import sys
import os

# Add the parent directory to the Python path to allow importing from 'models'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.quantum_algorithms import Grover, example_oracle_factory

class TestGroverAlgorithm(unittest.TestCase):
    """
    Test cases for the Grover's algorithm implementation.
    """

    def _run_grover_test(self, num_qubits, marked_item_index, expected_iterations=None):
        """
        Helper function to run a Grover search test.

        Args:
            num_qubits (int): The number of qubits for the search.
            marked_item_index (int): The index of the item to be marked by the oracle.
            expected_iterations (int, optional): If provided, Grover's algorithm will be run
                                                 for this many iterations. Otherwise, it uses
                                                 the optimal default.
        """
        print(f"\n--- Testing Grover with {num_qubits} qubits, marked item: {marked_item_index} ---")
        num_states = 2**num_qubits
        self.assertLess(marked_item_index, num_states, "Marked item index must be less than total number of states.")

        # 1. Create the oracle
        oracle_func = example_oracle_factory(
            marked_item_index=marked_item_index,
            num_total_items=num_states
        )

        # 2. Initialize Grover's algorithm
        grover_search = Grover(num_qubits=num_qubits, oracle_function=oracle_func)

        # 3. Run the algorithm
        if expected_iterations is not None:
            measured_index = grover_search.run_algorithm(num_iterations=expected_iterations)
            # Calculate optimal iterations for comparison if needed for assertion
            optimal_iterations = int(np.floor(np.pi / 4 * np.sqrt(num_states)))
            print(f"Ran with {expected_iterations} iterations. Optimal would be: {optimal_iterations}")
        else:
            measured_index = grover_search.run_algorithm() # Use optimal iterations

        # 4. Verify the result
        self.assertEqual(measured_index, marked_item_index,
                         f"Grover's algorithm did not find the marked item. "
                         f"Expected: {marked_item_index}, Got: {measured_index}")

        # 5. Verify probability amplification
        final_probabilities = grover_search.get_probabilities()
        probability_of_marked_item = final_probabilities[marked_item_index]
        
        print(f"Probability of marked item ({marked_item_index}): {probability_of_marked_item:.4f}")
        
        # For optimal iterations, probability should be high.
        # This threshold might need adjustment based on N and optimality of iterations.
        # For N=4 (2 qubits), 1 iter is optimal, P > 0.9
        # For N=8 (3 qubits), 2 iters are optimal, P > 0.9
        # For N=16 (4 qubits), 3 iters are optimal, P > 0.9
        # For N=32 (5 qubits), 6 iters are optimal, P > 0.9
        # If not using optimal iterations, this check might be less strict or different.
        if expected_iterations is None or expected_iterations == int(np.floor(np.pi / 4 * np.sqrt(num_states))):
             self.assertGreater(probability_of_marked_item, 0.9,
                               f"Probability of marked item {marked_item_index} ({probability_of_marked_item:.4f}) "
                               f"is not significantly high after optimal iterations.")
        elif num_qubits <=2 and expected_iterations == 1: # e.g. 2 qubits, 1 iteration is optimal
            self.assertGreater(probability_of_marked_item, 0.9,
                               f"Probability of marked item {marked_item_index} ({probability_of_marked_item:.4f}) "
                               f"is not significantly high.")
        
        # Check that other probabilities are low in comparison (optional, but good check)
        # for i, prob in enumerate(final_probabilities):
        #     if i != marked_item_index:
        #         self.assertLess(prob, probability_of_marked_item,
        #                         f"Probability of unmarked item {i} ({prob:.4f}) "
        #                         f"is not less than marked item's probability ({probability_of_marked_item:.4f}).")


    def test_finds_marked_item_2_qubits(self):
        """Test Grover's algorithm with 2 qubits, marked item 0. Optimal iterations = 1."""
        self._run_grover_test(num_qubits=2, marked_item_index=0) # Item |00>
        self._run_grover_test(num_qubits=2, marked_item_index=1) # Item |01>
        self._run_grover_test(num_qubits=2, marked_item_index=2) # Item |10>
        self._run_grover_test(num_qubits=2, marked_item_index=3) # Item |11>

    def test_finds_marked_item_3_qubits(self):
        """Test Grover's algorithm with 3 qubits. Optimal iterations = 2."""
        self._run_grover_test(num_qubits=3, marked_item_index=0)  # Item |000>
        self._run_grover_test(num_qubits=3, marked_item_index=5)  # Item |101>
        self._run_grover_test(num_qubits=3, marked_item_index=7)  # Item |111>
        
    def test_finds_marked_item_4_qubits(self):
        """Test Grover's algorithm with 4 qubits. Optimal iterations = 3."""
        self._run_grover_test(num_qubits=4, marked_item_index=0)   # Item |0000>
        self._run_grover_test(num_qubits=4, marked_item_index=13)  # Item |1101> (used in example)
        self._run_grover_test(num_qubits=4, marked_item_index=15)  # Item |1111>

    def test_finds_marked_item_5_qubits(self):
        """Test Grover's algorithm with 5 qubits. Optimal iterations = floor(pi/4 * sqrt(32)) = floor(pi/4 * 5.65) = floor(4.44) = 4."""
        # Note: The previous calculation for 5 qubits was floor(pi) = 3, which is incorrect.
        # Optimal for N=32 is floor(pi/4 * sqrt(32)) = floor(pi * sqrt(2)) approx floor(4.44) = 4 iterations.
        # The run_algorithm default is floor(pi/4 * sqrt(N)). Let's test with that.
        # For 5 qubits, N=32, sqrt(N) approx 5.656. (pi/4)*sqrt(N) approx 4.44. floor is 4.
        self._run_grover_test(num_qubits=5, marked_item_index=0)
        self._run_grover_test(num_qubits=5, marked_item_index=17) # Example item |10001>
        self._run_grover_test(num_qubits=5, marked_item_index=31)

    def test_specific_iterations_3_qubits(self):
        """
        Test with 3 qubits and a specific number of iterations.
        Optimal for N=8 (3 qubits) is floor(pi/4 * sqrt(8)) = 2 iterations.
        One iteration should still amplify, but not as much as two.
        """
        # With 1 iteration (sub-optimal) for 3 qubits
        # The main assertion is that it finds the item. Probability check might be less strict.
        num_qubits = 3
        marked_item_index = 2 # |010>
        num_states = 2**num_qubits
        oracle_func = example_oracle_factory(marked_item_index, num_states)
        grover_search = Grover(num_qubits, oracle_func)
        
        measured_index = grover_search.run_algorithm(num_iterations=1)
        self.assertEqual(measured_index, marked_item_index,
                         "Grover (3 qubits, 1 iter) did not find marked item 2.")
        
        prob_marked_item = grover_search.get_probabilities()[marked_item_index]
        print(f"Probability of item {marked_item_index} after 1 iter (3 qubits): {prob_marked_item:.4f}")
        # After 1 iteration for N=8, probability of target is ( (2*k/N -1) + 1/sqrt(N) )^2 where k=1
        # Oracle flips, diffuser reflects.
        # Initial state: all 1/sqrt(N). Mean = 1/sqrt(N).
        # Oracle: marked = -1/sqrt(N), others = 1/sqrt(N).
        # Mean_after_oracle = ( (N-1)/sqrt(N) - 1/sqrt(N) ) / N = (N-2)/(N*sqrt(N))
        # Diffuser:
        #   marked_new = 2*mean_after_oracle - (-1/sqrt(N)) = 2(N-2)/(N*sqrt(N)) + 1/sqrt(N)
        #              = (2N - 4 + N) / (N*sqrt(N)) = (3N-4)/(N*sqrt(N))
        # For N=8, marked_new = (24-4)/(8*sqrt(8)) = 20 / (16*sqrt(2)) = 5 / (4*sqrt(2)) = 5*sqrt(2)/8 approx 0.8838
        # Probability = (5*sqrt(2)/8)^2 = (25*2)/64 = 50/64 = 25/32 = 0.78125
        self.assertAlmostEqual(prob_marked_item, 0.78125, places=4,
                               msg=f"Probability of marked item {marked_item_index} after 1 iter (3 qubits) "
                                   f"was {prob_marked_item:.4f}, expected ~0.78125.")

        # With 2 iterations (optimal) for 3 qubits
        grover_search_optimal = Grover(num_qubits, oracle_func) # Re-initialize
        measured_index_optimal = grover_search_optimal.run_algorithm(num_iterations=2)
        self.assertEqual(measured_index_optimal, marked_item_index,
                         "Grover (3 qubits, 2 iters) did not find marked item 2.")
        prob_marked_item_optimal = grover_search_optimal.get_probabilities()[marked_item_index]
        print(f"Probability of item {marked_item_index} after 2 iters (3 qubits): {prob_marked_item_optimal:.4f}")
        # For N=8, 2 iterations is optimal, prob should be very high, close to 1.
        # Theoretical max is sin^2((2k+1)theta) where sin(theta)=1/sqrt(N). For k=2, sin^2(5*theta).
        # Theta = asin(1/sqrt(8)) = asin(0.3535) ~ 20.7 degrees. 5*theta ~ 103.5 degrees. sin(103.5) ~ 0.972. prob ~ 0.945.
        # The implementation's calculation of optimal iterations is floor(pi/4 * sqrt(N)).
        # For N=8, this is floor(pi/4 * 2.828) = floor(2.22) = 2.
        # So, this should be an optimal run.
        self.assertGreater(prob_marked_item_optimal, 0.94, # Based on calculation
                           f"Probability ({prob_marked_item_optimal:.4f}) after 2 optimal iterations (3 qubits) too low.")


    def test_invalid_inputs(self):
        """Test Grover's algorithm with invalid inputs to the constructor."""
        with self.assertRaisesRegex(ValueError, "Number of qubits must be a positive integer."):
            Grover(num_qubits=0, oracle_function=lambda x: False)
        with self.assertRaisesRegex(ValueError, "Number of qubits must be a positive integer."):
            Grover(num_qubits=-1, oracle_function=lambda x: False)
        with self.assertRaisesRegex(TypeError, "oracle_function must be a callable function."):
            Grover(num_qubits=2, oracle_function="not a function")

        # Test invalid marked_item_index for oracle factory
        with self.assertRaisesRegex(ValueError, "marked_item_index .* is out of bounds"):
            example_oracle_factory(marked_item_index=4, num_total_items=4) # Max index is 3 for 4 items
        with self.assertRaisesRegex(ValueError, "marked_item_index .* is out of bounds"):
            example_oracle_factory(marked_item_index=-1, num_total_items=4)

        # Test invalid num_iterations for run_algorithm
        grover = Grover(num_qubits=2, oracle_function=example_oracle_factory(0, 4))
        with self.assertRaisesRegex(ValueError, "Number of iterations must be a non-negative integer."):
            grover.run_algorithm(num_iterations=-1)


if __name__ == '__main__':
    unittest.main(verbosity=2)

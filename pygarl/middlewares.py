from __future__ import print_function
from pygarl.base import Sample
from pygarl.abstracts import AbstractMiddleware
import numpy as np


class GradientThresholdMiddleware(AbstractMiddleware):
    # TODO: tests and documentation
    def __init__(self, threshold=10, group=True, sample_group_delay=2, verbose=False):
        """
        Class constructor
        :param threshold: The value that must be crossed to mark a sample as valid.
                          The higher the value, the most intense the movement must be to
                          pass the middleware.
                          
        :param group:     If True, the middleware tries to group samples belonging to the same movement
                          into one sample.
                          
        :param: sample_group_delay: The amount of samples that are included in the grouped sample that
                                    have not crossed the threshold. This is useful because sometimes
                                    samples have some oscillations that make the middleware split
                                    samples even if they belong to the same one.
        
        :param verbose:   If True, prints more information
        """
        # Call the base constructor
        AbstractMiddleware.__init__(self)

        # Set the parameters
        self.threshold = threshold
        self.verbose = verbose
        self.group = group
        self.sample_group_delay = sample_group_delay

        # Create the array that will hold the sample data to be grouped
        # Initially it is None
        self.buffer = None

        # Counter for the sample_group_delay property
        self.sample_group_delay_counter = 0

    def add_sample_to_buffer(self, sample):
        """
        Add the given sample to the buffer to group them.
        :param sample: Sample to add.
        """
        # Get a copy of the sample data
        sample_data = np.array(sample.data, copy=True)

        # If buffer is empty, it becomes equal to the sample data
        if self.buffer is None:
            self.buffer = sample_data
        else:  # buffer is not empty, concatenate the new sample data
            self.buffer = np.concatenate((self.buffer, sample_data))

    def delete_buffer(self):
        """
        Delete the current buffer by setting it to None
        """
        self.buffer = None

    def process_sample(self, sample):
        # Get the sample gradient
        gradient = sample.gradient()

        # Calculate the average
        average = np.average(gradient)

        # Calculate the absolute value
        average = np.absolute(average)

        # If verbose, print the average
        if self.verbose:
            print("GTM Average:", average)

        # If true, the sample will pass.
        is_allowed_to_pass = False

        # If the average is bigger than the threshold, return the sample
        # If not, suppress the sample by returning None
        if average >= self.threshold:
            is_allowed_to_pass = True

            # Reset the sample_group_delay counter
            self.sample_group_delay_counter = 0
        else:
            if self.group and self.sample_group_delay_counter < self.sample_group_delay:
                is_allowed_to_pass = True

                # Increase the sample_group_delay counter
                self.sample_group_delay_counter += 1

        if is_allowed_to_pass:
            # If grouping is not enabled, return the sample directly
            if not self.group:
                return sample
            else:  # grouping is enabled, return None and add the current sample to the buffer
                self.add_sample_to_buffer(sample)

                # If verbose, print some info
                if self.verbose:
                    print("GTM:", "Suppressed sample to be grouped.")

                # Suppress the single sample
                return None
        else:
            # If grouping is not enabled, suppress the sample
            if not self.group:
                # Suppress the Sample
                return None
            else:  # Grouping is enabled
                # Check that the buffer is not empty
                if self.buffer is not None:
                    # If this sample has not crossed the threshold it means that the grouped sample
                    # is finished and can be returned.

                    # Copy the buffer
                    grouped_data = np.copy(self.buffer)

                    # Delete the buffer
                    self.delete_buffer()

                    # Create a new sample with the grouped data
                    new_sample = Sample(data=grouped_data, gesture_id=sample.gesture_id)

                    # Return the new sample
                    return new_sample
                else:  # Buffer empty, return none
                    return None


class DelayGrouperMiddleware(AbstractMiddleware):
    """
    Group received samples into one Sample if they arrive within "delay" time from one another.
    Useful to group individual samples spawned by the GradientThresholdMiddleware that belongs
    to the same gesture.
    """
    def __init__(self, delay=300):
        """
        Class constructor
        :param delay: Milliseconds between samples that must be grouped.
        """
        # Call the base constructor
        AbstractMiddleware.__init__(self)

        # Set the parameters
        self.delay = delay

    def process_sample(self, sample):
        # Not implemented yet
        raise NotImplementedError("DelayGrouperMiddleware is not implemented yet")


class PlotterMiddleware(AbstractMiddleware):
    """
    Used to plot sample after being received
    """
    def __init__(self):
        # Call the base constructor
        AbstractMiddleware.__init__(self)

    def process_sample(self, sample):
        """
        Plot the sample and return it
        :param sample: sample to plot
        """
        # Plot the sample
        sample.plot()

        return sample
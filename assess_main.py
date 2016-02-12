import argparse
import logging

from utility.report import update_parser, argparse_init, LVL
from utility.exceptions import mainExceptionFrame

from assess.prototypes.simpleprototypes import prototype_one, prototype_two
from assess.algorithms.incrementaldistancealgorithm import IncrementalDistanceAlgorithm
from assess.algorithms.incrementalstructuredistancealgorithm import IncrementalStructureDistanceAlgorithm
from assess.algorithms.treeinclusiondistancealgorithm import TreeInclusionDistanceAlgorithm
from assess.events.events import ProcessStartEvent, ProcessExitEvent
from assess.decorators.distancematrixdecorator import DistanceMatrixDecorator


def main():
    test = prototype_one()
    test2 = prototype_two()
    decorator = DistanceMatrixDecorator(normalized=True)
    alg = IncrementalDistanceAlgorithm()
    alg.prototypes = [test, test2]
    decorator.algorithm = alg
    decorator.add_event(ProcessStartEvent(0, 1, 1, name="root"))
    decorator.add_event(ProcessStartEvent(0, 6, 1, name="test"))
    decorator.add_event(ProcessStartEvent(0, 2, 6, name="ls"))
    decorator.add_event(ProcessStartEvent(0, 3, 1, name="wget"))
    decorator.add_event(ProcessStartEvent(0, 4, 2, name="mv"))
    decorator.add_event(ProcessStartEvent(0, 5, 2, name="rm"))
    decorator.add_event(ProcessExitEvent(0, 5, 2, 0, name="rm"))
    decorator.add_event(ProcessExitEvent(0, 4, 2, 0, name="mv"))
    decorator.add_event(ProcessExitEvent(0, 3, 1, 0, name="wget"))
    decorator.add_event(ProcessExitEvent(0, 2, 1, 0, name="ls"))
    decorator.add_event(ProcessExitEvent(0, 1, 1, 0, name="root"))
    print("distance matrix %s" % decorator.distance_matrix)

    alg2 = IncrementalStructureDistanceAlgorithm()
    alg2.prototypes = [test, test2]
    alg2.add_event(ProcessStartEvent(0, 1, 1, name="root"))
    alg2.add_event(ProcessStartEvent(0, 6, 1, name="test"))
    alg2.add_event(ProcessStartEvent(0, 2, 6, name="ls"))
    alg2.add_event(ProcessStartEvent(0, 3, 1, name="wget"))
    alg2.add_event(ProcessStartEvent(0, 4, 2, name="mv"))
    alg2.add_event(ProcessStartEvent(0, 5, 2, name="rm"))
    alg2.add_event(ProcessExitEvent(0, 5, 2, 0, name="rm"))
    alg2.add_event(ProcessExitEvent(0, 4, 2, 0, name="mv"))
    alg2.add_event(ProcessExitEvent(0, 3, 1, 0, name="wget"))
    alg2.add_event(ProcessExitEvent(0, 2, 1, 0, name="ls"))
    alg2.add_event(ProcessExitEvent(0, 1, 1, 0, name="root"))

    print("Starting to measure tree inclusion distance")
    alg3 = TreeInclusionDistanceAlgorithm()
    alg3.prototypes = [test, test2]
    print("measured distance: %s" % alg3.add_event(ProcessStartEvent(0, 1, 1, name="root")))
    print("measured distance: %s" % alg3.add_event(ProcessStartEvent(0, 6, 1, name="test")))
    print("measured distance: %s" % alg3.add_event(ProcessStartEvent(0, 2, 6, name="ls")))
    print("measured distance: %s" % alg3.add_event(ProcessStartEvent(0, 3, 1, name="wget")))
    print("measured distance: %s" % alg3.add_event(ProcessStartEvent(0, 4, 2, name="mv")))
    print("measured distance: %s" % alg3.add_event(ProcessStartEvent(0, 5, 2, name="rm")))
    alg3.add_event(ProcessExitEvent(0, 5, 2, 0, name="rm"))
    alg3.add_event(ProcessExitEvent(0, 4, 2, 0, name="mv"))
    alg3.add_event(ProcessExitEvent(0, 3, 1, 0, name="wget"))
    alg3.add_event(ProcessExitEvent(0, 2, 1, 0, name="ls"))
    alg3.add_event(ProcessExitEvent(0, 1, 1, 0, name="root"))

if __name__ == '__main__':
    cli = argparse.ArgumentParser()
    update_parser(cli)
    argparse_init(cli.parse_args())

    logging.getLogger().setLevel(LVL.WARNING)
    logging.getLogger("EXCEPTION").setLevel(LVL.INFO)
    mainExceptionFrame(main)

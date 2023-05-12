import logging
from bawsys import testScenarioAsserter as scenAssert

#=========================================================================
def executeAsserts(asserter: scenAssert.ScenarioAsserter, listOfInstances):

    logging.info("======> executeAsserts, tot instances: %d", len(listOfInstances))

    asserter.assertItemsCountEquals(listOfInstances, 1)
    asserter.assertEqual(listOfInstances, "variables.promoteRequest", "true")


import logging, json
from bawsys import testScenarioAsserter as scenAssert

#=========================================================================
def executeAsserts(asserter: scenAssert.ScenarioAsserter, listOfInstances):

    logging.info("======> executeAsserts, tot instances: %d %s", len(listOfInstances), json.dumps(listOfInstances, indent=2))

    asserter.assertItemsCountEquals(listOfInstances, 1)
    asserter.assertItemsCountNotEquals(listOfInstances, 2)
    asserter.assertEqual(listOfInstances, "variables.promoteRequest", "true")
    asserter.assertNotEqual(listOfInstances, "variables.promoteRequest", "false")

    asserter.assertEqual(listOfInstances, "variables.evaluationForm.vote", 6)
    asserter.assertNotEqual(listOfInstances, "variables.evaluationForm.vote", 60)
    asserter.assertLesserThan(listOfInstances, "variables.evaluationForm.vote", 10)
    asserter.assertLesserEqualThan(listOfInstances, "variables.evaluationForm.vote", 10)
    asserter.assertGreaterThan(listOfInstances, "variables.evaluationForm.vote", 0)
    asserter.assertGreaterEqualThan(listOfInstances, "variables.evaluationForm.vote", 0)

    #asserter.assertItemsCountEquals(listOfInstances, 2)
    #asserter.assertEqual(listOfInstances, "variables.promoteRequest", "false")


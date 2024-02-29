"""
Model exported as python.
Name : OD Matrices
Group : Graduate School
With QGIS : 32216
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterMapLayer
from qgis.core import QgsProcessingParameterExpression
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class OdMatrices(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterMapLayer('countycentroids', 'County Centroids', defaultValue=None, types=[QgsProcessing.TypeVectorPoint]))
        self.addParameter(QgsProcessingParameterMapLayer('mills', 'Mills', defaultValue=None, types=[QgsProcessing.TypeVectorPoint]))
        self.addParameter(QgsProcessingParameterMapLayer('roadnetwork', 'Road Network', defaultValue=None, types=[QgsProcessing.TypeVectorLine]))
        self.addParameter(QgsProcessingParameterExpression('selectbylogsort', 'Select by Log Sort', parentLayerParameterName='', defaultValue=''))
        self.addParameter(QgsProcessingParameterExpression('selectbylogsort (2)', 'Select County', parentLayerParameterName='', defaultValue=''))
        self.addParameter(QgsProcessingParameterFeatureSink('County_mill', 'county_mill', type=QgsProcessing.TypeVectorLine, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(3, model_feedback)
        results = {}
        outputs = {}

        # Select by expression
        alg_params = {
            'EXPRESSION': parameters['selectbylogsort'],
            'INPUT': parameters['mills'],
            'METHOD': 0,  # creating new selection
        }
        outputs['SelectByExpression'] = processing.run('qgis:selectbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # OD Matrix from Layers as Table (m:n)
        alg_params = {
            'DEFAULT_DIRECTION': 2,  # Both directions
            'DEFAULT_SPEED': 5,
            'DIRECTION_FIELD': 'oneway',
            'ENTRY_COST_CALCULATION_METHOD': 0,  # Ellipsoidal
            'FROM_ID_FIELD': 'county_nam',
            'FROM_POINT_LAYER': parameters['selectbylogsort (2)'],
            'INPUT': parameters['roadnetwork'],
            'SPEED_FIELD': 'maxspeed',
            'STRATEGY': 0,  # Shortest Path (distance optimization)
            'TOLERANCE': 0,
            'TO_ID_FIELD': 'FID',
            'TO_POINT_LAYER': parameters['selectbylogsort'],
            'VALUE_BACKWARD': 'T',
            'VALUE_BOTH': 'B',
            'VALUE_FORWARD': 'F',
            'OUTPUT': parameters['County_mill']
        }
        outputs['OdMatrixFromLayersAsTableMn'] = processing.run('qneat3:OdMatrixFromLayersAsTable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['County_mill'] = outputs['OdMatrixFromLayersAsTableMn']['OUTPUT']

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Select by expression
        alg_params = {
            'EXPRESSION': parameters['selectbylogsort (2)'],
            'INPUT': parameters['countycentroids'],
            'METHOD': 0,  # creating new selection
        }
        outputs['SelectByExpression'] = processing.run('qgis:selectbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        return results

    def name(self):
        return 'OD Matrices'

    def displayName(self):
        return 'OD Matrices'

    def group(self):
        return 'Graduate School'

    def groupId(self):
        return 'Graduate School'

    def createInstance(self):
        return OdMatrices()

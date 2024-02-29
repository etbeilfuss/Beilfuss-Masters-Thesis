"""
Model exported as python.
Name : Bolt Isochrones
Group : Graduate School
With QGIS : 32216
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class BoltIsochrones(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('landforms', 'Landforms', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('mills', 'Mills', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('roadnetwork', 'Road Network', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Balsamfir', 'BalsamFir', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue='TEMPORARY_OUTPUT'))
        self.addParameter(QgsProcessingParameterFeatureSink('Basswood', 'Basswood', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('BlackLocust', 'Black Locust', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Boxelder', 'Boxelder', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('RedOak', 'Red Oak', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Tamarack', 'Tamarack', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('WhiteOak', 'White Oak', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('WhitePine', 'White Pine', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(48, model_feedback)
        results = {}
        outputs = {}

        # BalsamFir Accepting Mills
        alg_params = {
            'EXPRESSION': '"b.BalsamFir" > 0',
            'INPUT': parameters['mills'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['BalsamfirAcceptingMills'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # BalsamFir Isochrones
        alg_params = {
            'CELL_SIZE': 10000,
            'DEFAULT_DIRECTION': 2,  # Both directions
            'DEFAULT_SPEED': 5,
            'DIRECTION_FIELD': 'oneway',
            'ENTRY_COST_CALCULATION_METHOD': 0,  # Planar (only use with projected CRS)
            'ID_FIELD': 'new_id',
            'INPUT': parameters['roadnetwork'],
            'INTERVAL': 41842.94,
            'MAX_DIST': 127138.2,
            'SPEED_FIELD': '',
            'START_POINTS': outputs['BalsamfirAcceptingMills']['OUTPUT'],
            'STRATEGY': 0,  # Shortest Path (distance optimization)
            'TOLERANCE': 0,
            'VALUE_BACKWARD': 'T',
            'VALUE_BOTH': 'B',
            'VALUE_FORWARD': 'F',
            'OUTPUT_INTERPOLATION': QgsProcessing.TEMPORARY_OUTPUT,
            'OUTPUT_POLYGONS': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['BalsamfirIsochrones'] = processing.run('qneat3:isoareaaspolygonsfromlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Clip Landforms BalsamFir
        alg_params = {
            'INPUT': outputs['BalsamfirIsochrones']['OUTPUT_POLYGONS'],
            'OVERLAY': parameters['landforms'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ClipLandformsBalsamfir'] = processing.run('native:clip', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Multipart to singleparts BalsamFir
        alg_params = {
            'INPUT': outputs['ClipLandformsBalsamfir']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MultipartToSinglepartsBalsamfir'] = processing.run('native:multiparttosingleparts', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Extract by location BalsamFir
        alg_params = {
            'INPUT': outputs['MultipartToSinglepartsBalsamfir']['OUTPUT'],
            'INTERSECT': outputs['BalsamfirAcceptingMills']['OUTPUT'],
            'PREDICATE': [0],  # intersect
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByLocationBalsamfir'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Add Species Field BalsamFir
        alg_params = {
            'FIELD_LENGTH': 20,
            'FIELD_NAME': 'Species',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # String
            'FORMULA': "'BalsamFir'",
            'INPUT': outputs['ExtractByLocationBalsamfir']['OUTPUT'],
            'OUTPUT': parameters['Balsamfir']
        }
        outputs['AddSpeciesFieldBalsamfir'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Balsamfir'] = outputs['AddSpeciesFieldBalsamfir']['OUTPUT']

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Basswood Accepting Mills
        alg_params = {
            'EXPRESSION': '"b.Basswood" > 0',
            'INPUT': parameters['mills'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['BasswoodAcceptingMills'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Basswood Isochrones
        alg_params = {
            'CELL_SIZE': 10000,
            'DEFAULT_DIRECTION': 2,  # Both directions
            'DEFAULT_SPEED': 5,
            'DIRECTION_FIELD': 'oneway',
            'ENTRY_COST_CALCULATION_METHOD': 0,  # Planar (only use with projected CRS)
            'ID_FIELD': 'new_id',
            'INPUT': parameters['roadnetwork'],
            'INTERVAL': 41842.94,
            'MAX_DIST': 127138.2,
            'SPEED_FIELD': '',
            'START_POINTS': outputs['BasswoodAcceptingMills']['OUTPUT'],
            'STRATEGY': 0,  # Shortest Path (distance optimization)
            'TOLERANCE': 0,
            'VALUE_BACKWARD': 'T',
            'VALUE_BOTH': 'B',
            'VALUE_FORWARD': 'F',
            'OUTPUT_INTERPOLATION': QgsProcessing.TEMPORARY_OUTPUT,
            'OUTPUT_POLYGONS': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['BasswoodIsochrones'] = processing.run('qneat3:isoareaaspolygonsfromlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Clip Landforms Basswood
        alg_params = {
            'INPUT': outputs['BasswoodIsochrones']['OUTPUT_POLYGONS'],
            'OVERLAY': parameters['landforms'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ClipLandformsBasswood'] = processing.run('native:clip', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Multipart to singleparts Basswood
        alg_params = {
            'INPUT': outputs['ClipLandformsBasswood']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MultipartToSinglepartsBasswood'] = processing.run('native:multiparttosingleparts', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # Extract by location Basswood
        alg_params = {
            'INPUT': outputs['MultipartToSinglepartsBasswood']['OUTPUT'],
            'INTERSECT': outputs['BasswoodAcceptingMills']['OUTPUT'],
            'PREDICATE': [0],  # intersect
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByLocationBasswood'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # Add Species Field Basswood
        alg_params = {
            'FIELD_LENGTH': 20,
            'FIELD_NAME': 'Species',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # String
            'FORMULA': "'Basswood'",
            'INPUT': outputs['ExtractByLocationBasswood']['OUTPUT'],
            'OUTPUT': parameters['Basswood']
        }
        outputs['AddSpeciesFieldBasswood'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Basswood'] = outputs['AddSpeciesFieldBasswood']['OUTPUT']

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # Blocust Accepting Mills
        alg_params = {
            'EXPRESSION': '"b.Blocust" > 0',
            'INPUT': parameters['mills'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['BlocustAcceptingMills'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(13)
        if feedback.isCanceled():
            return {}

        # Blocust Isochrones
        alg_params = {
            'CELL_SIZE': 10000,
            'DEFAULT_DIRECTION': 2,  # Both directions
            'DEFAULT_SPEED': 5,
            'DIRECTION_FIELD': 'oneway',
            'ENTRY_COST_CALCULATION_METHOD': 0,  # Planar (only use with projected CRS)
            'ID_FIELD': 'new_id',
            'INPUT': parameters['roadnetwork'],
            'INTERVAL': 41842.94,
            'MAX_DIST': 127138.2,
            'SPEED_FIELD': '',
            'START_POINTS': outputs['BlocustAcceptingMills']['OUTPUT'],
            'STRATEGY': 0,  # Shortest Path (distance optimization)
            'TOLERANCE': 0,
            'VALUE_BACKWARD': 'T',
            'VALUE_BOTH': 'B',
            'VALUE_FORWARD': 'F',
            'OUTPUT_INTERPOLATION': QgsProcessing.TEMPORARY_OUTPUT,
            'OUTPUT_POLYGONS': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['BlocustIsochrones'] = processing.run('qneat3:isoareaaspolygonsfromlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(14)
        if feedback.isCanceled():
            return {}

        # Clip Landforms Blocust
        alg_params = {
            'INPUT': outputs['BlocustIsochrones']['OUTPUT_POLYGONS'],
            'OVERLAY': parameters['landforms'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ClipLandformsBlocust'] = processing.run('native:clip', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(15)
        if feedback.isCanceled():
            return {}

        # Multipart to singleparts Blocust
        alg_params = {
            'INPUT': outputs['ClipLandformsBlocust']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MultipartToSinglepartsBlocust'] = processing.run('native:multiparttosingleparts', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(16)
        if feedback.isCanceled():
            return {}

        # Extract by location Blocust
        alg_params = {
            'INPUT': outputs['MultipartToSinglepartsBlocust']['OUTPUT'],
            'INTERSECT': outputs['BlocustAcceptingMills']['OUTPUT'],
            'PREDICATE': [0],  # intersect
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByLocationBlocust'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(17)
        if feedback.isCanceled():
            return {}

        # Add Species Field Blocust
        alg_params = {
            'FIELD_LENGTH': 20,
            'FIELD_NAME': 'Species',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # String
            'FORMULA': "'Blocust'",
            'INPUT': outputs['ExtractByLocationBlocust']['OUTPUT'],
            'OUTPUT': parameters['BlackLocust']
        }
        outputs['AddSpeciesFieldBlocust'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['BlackLocust'] = outputs['AddSpeciesFieldBlocust']['OUTPUT']

        feedback.setCurrentStep(18)
        if feedback.isCanceled():
            return {}

        # Boxelder Accepting Mills
        alg_params = {
            'EXPRESSION': '"b.Boxelder" > 0',
            'INPUT': parameters['mills'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['BoxelderAcceptingMills'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(19)
        if feedback.isCanceled():
            return {}

        # Boxelder Isochrones
        alg_params = {
            'CELL_SIZE': 10000,
            'DEFAULT_DIRECTION': 2,  # Both directions
            'DEFAULT_SPEED': 5,
            'DIRECTION_FIELD': 'oneway',
            'ENTRY_COST_CALCULATION_METHOD': 0,  # Planar (only use with projected CRS)
            'ID_FIELD': 'new_id',
            'INPUT': parameters['roadnetwork'],
            'INTERVAL': 41842.94,
            'MAX_DIST': 127138.2,
            'SPEED_FIELD': '',
            'START_POINTS': outputs['BoxelderAcceptingMills']['OUTPUT'],
            'STRATEGY': 0,  # Shortest Path (distance optimization)
            'TOLERANCE': 0,
            'VALUE_BACKWARD': 'T',
            'VALUE_BOTH': 'B',
            'VALUE_FORWARD': 'F',
            'OUTPUT_INTERPOLATION': QgsProcessing.TEMPORARY_OUTPUT,
            'OUTPUT_POLYGONS': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['BoxelderIsochrones'] = processing.run('qneat3:isoareaaspolygonsfromlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(20)
        if feedback.isCanceled():
            return {}

        # Clip Landforms .Boxelder
        alg_params = {
            'INPUT': outputs['BoxelderIsochrones']['OUTPUT_POLYGONS'],
            'OVERLAY': parameters['landforms'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ClipLandformsBoxelder'] = processing.run('native:clip', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(21)
        if feedback.isCanceled():
            return {}

        # Multipart to singleparts Boxelder
        alg_params = {
            'INPUT': outputs['ClipLandformsBoxelder']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MultipartToSinglepartsBoxelder'] = processing.run('native:multiparttosingleparts', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(22)
        if feedback.isCanceled():
            return {}

        # Extract by location Boxelder
        alg_params = {
            'INPUT': outputs['MultipartToSinglepartsBoxelder']['OUTPUT'],
            'INTERSECT': outputs['BoxelderAcceptingMills']['OUTPUT'],
            'PREDICATE': [0],  # intersect
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByLocationBoxelder'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(23)
        if feedback.isCanceled():
            return {}

        # Add Species Field Boxelder
        alg_params = {
            'FIELD_LENGTH': 20,
            'FIELD_NAME': 'Species',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # String
            'FORMULA': "'Boxelder'",
            'INPUT': outputs['ExtractByLocationBoxelder']['OUTPUT'],
            'OUTPUT': parameters['Boxelder']
        }
        outputs['AddSpeciesFieldBoxelder'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Boxelder'] = outputs['AddSpeciesFieldBoxelder']['OUTPUT']

        feedback.setCurrentStep(24)
        if feedback.isCanceled():
            return {}

        # RedOak Accepting Mills
        alg_params = {
            'EXPRESSION': '"b.RedOak" > 0',
            'INPUT': parameters['mills'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RedoakAcceptingMills'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(25)
        if feedback.isCanceled():
            return {}

        # RedOak Isochrones
        alg_params = {
            'CELL_SIZE': 10000,
            'DEFAULT_DIRECTION': 2,  # Both directions
            'DEFAULT_SPEED': 5,
            'DIRECTION_FIELD': 'oneway',
            'ENTRY_COST_CALCULATION_METHOD': 0,  # Planar (only use with projected CRS)
            'ID_FIELD': 'new_id',
            'INPUT': parameters['roadnetwork'],
            'INTERVAL': 41842.94,
            'MAX_DIST': 127138.2,
            'SPEED_FIELD': '',
            'START_POINTS': outputs['RedoakAcceptingMills']['OUTPUT'],
            'STRATEGY': 0,  # Shortest Path (distance optimization)
            'TOLERANCE': 0,
            'VALUE_BACKWARD': 'T',
            'VALUE_BOTH': 'B',
            'VALUE_FORWARD': 'F',
            'OUTPUT_INTERPOLATION': QgsProcessing.TEMPORARY_OUTPUT,
            'OUTPUT_POLYGONS': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RedoakIsochrones'] = processing.run('qneat3:isoareaaspolygonsfromlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(26)
        if feedback.isCanceled():
            return {}

        # Clip Landforms RedOak
        alg_params = {
            'INPUT': outputs['RedoakIsochrones']['OUTPUT_POLYGONS'],
            'OVERLAY': parameters['landforms'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ClipLandformsRedoak'] = processing.run('native:clip', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(27)
        if feedback.isCanceled():
            return {}

        # Multipart to singleparts RedOak
        alg_params = {
            'INPUT': outputs['ClipLandformsRedoak']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MultipartToSinglepartsRedoak'] = processing.run('native:multiparttosingleparts', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(28)
        if feedback.isCanceled():
            return {}

        # Extract by location RedOak
        alg_params = {
            'INPUT': outputs['MultipartToSinglepartsRedoak']['OUTPUT'],
            'INTERSECT': outputs['RedoakAcceptingMills']['OUTPUT'],
            'PREDICATE': [0],  # intersect
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByLocationRedoak'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(29)
        if feedback.isCanceled():
            return {}

        # Add Species Field RedOak
        alg_params = {
            'FIELD_LENGTH': 20,
            'FIELD_NAME': 'Species',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # String
            'FORMULA': "'RedOak'",
            'INPUT': outputs['ExtractByLocationRedoak']['OUTPUT'],
            'OUTPUT': parameters['RedOak']
        }
        outputs['AddSpeciesFieldRedoak'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['RedOak'] = outputs['AddSpeciesFieldRedoak']['OUTPUT']

        feedback.setCurrentStep(30)
        if feedback.isCanceled():
            return {}

        # Tamarack Accepting Mills
        alg_params = {
            'EXPRESSION': '"b.Tamarack" > 0',
            'INPUT': parameters['mills'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['TamarackAcceptingMills'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(31)
        if feedback.isCanceled():
            return {}

        # Tamarack Isochrones
        alg_params = {
            'CELL_SIZE': 10000,
            'DEFAULT_DIRECTION': 2,  # Both directions
            'DEFAULT_SPEED': 5,
            'DIRECTION_FIELD': 'oneway',
            'ENTRY_COST_CALCULATION_METHOD': 0,  # Planar (only use with projected CRS)
            'ID_FIELD': 'new_id',
            'INPUT': parameters['roadnetwork'],
            'INTERVAL': 41842.94,
            'MAX_DIST': 127138.2,
            'SPEED_FIELD': '',
            'START_POINTS': outputs['TamarackAcceptingMills']['OUTPUT'],
            'STRATEGY': 0,  # Shortest Path (distance optimization)
            'TOLERANCE': 0,
            'VALUE_BACKWARD': 'T',
            'VALUE_BOTH': 'B',
            'VALUE_FORWARD': 'F',
            'OUTPUT_INTERPOLATION': QgsProcessing.TEMPORARY_OUTPUT,
            'OUTPUT_POLYGONS': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['TamarackIsochrones'] = processing.run('qneat3:isoareaaspolygonsfromlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(32)
        if feedback.isCanceled():
            return {}

        # Clip Landforms Tamarack
        alg_params = {
            'INPUT': outputs['TamarackIsochrones']['OUTPUT_POLYGONS'],
            'OVERLAY': parameters['landforms'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ClipLandformsTamarack'] = processing.run('native:clip', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(33)
        if feedback.isCanceled():
            return {}

        # Multipart to singleparts Tamarack
        alg_params = {
            'INPUT': outputs['ClipLandformsTamarack']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MultipartToSinglepartsTamarack'] = processing.run('native:multiparttosingleparts', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(34)
        if feedback.isCanceled():
            return {}

        # Extract by location Tamarack
        alg_params = {
            'INPUT': outputs['MultipartToSinglepartsTamarack']['OUTPUT'],
            'INTERSECT': outputs['TamarackAcceptingMills']['OUTPUT'],
            'PREDICATE': [0],  # intersect
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByLocationTamarack'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(35)
        if feedback.isCanceled():
            return {}

        # Add Species Field Tamarack
        alg_params = {
            'FIELD_LENGTH': 20,
            'FIELD_NAME': 'Species',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # String
            'FORMULA': "'Tamarack'",
            'INPUT': outputs['ExtractByLocationTamarack']['OUTPUT'],
            'OUTPUT': parameters['Tamarack']
        }
        outputs['AddSpeciesFieldTamarack'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Tamarack'] = outputs['AddSpeciesFieldTamarack']['OUTPUT']

        feedback.setCurrentStep(36)
        if feedback.isCanceled():
            return {}

        # WhiteOak Accepting Mills
        alg_params = {
            'EXPRESSION': '"b.WhiteOak" > 0',
            'INPUT': parameters['mills'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['WhiteoakAcceptingMills'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(37)
        if feedback.isCanceled():
            return {}

        # WhiteOak Isochrones
        alg_params = {
            'CELL_SIZE': 10000,
            'DEFAULT_DIRECTION': 2,  # Both directions
            'DEFAULT_SPEED': 5,
            'DIRECTION_FIELD': 'oneway',
            'ENTRY_COST_CALCULATION_METHOD': 0,  # Planar (only use with projected CRS)
            'ID_FIELD': 'new_id',
            'INPUT': parameters['roadnetwork'],
            'INTERVAL': 41842.94,
            'MAX_DIST': 127138.2,
            'SPEED_FIELD': '',
            'START_POINTS': outputs['WhiteoakAcceptingMills']['OUTPUT'],
            'STRATEGY': 0,  # Shortest Path (distance optimization)
            'TOLERANCE': 0,
            'VALUE_BACKWARD': 'T',
            'VALUE_BOTH': 'B',
            'VALUE_FORWARD': 'F',
            'OUTPUT_INTERPOLATION': QgsProcessing.TEMPORARY_OUTPUT,
            'OUTPUT_POLYGONS': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['WhiteoakIsochrones'] = processing.run('qneat3:isoareaaspolygonsfromlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(38)
        if feedback.isCanceled():
            return {}

        # Clip Landforms WhiteOak
        alg_params = {
            'INPUT': outputs['WhiteoakIsochrones']['OUTPUT_POLYGONS'],
            'OVERLAY': parameters['landforms'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ClipLandformsWhiteoak'] = processing.run('native:clip', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(39)
        if feedback.isCanceled():
            return {}

        # Multipart to singleparts WhiteOak
        alg_params = {
            'INPUT': outputs['ClipLandformsWhiteoak']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MultipartToSinglepartsWhiteoak'] = processing.run('native:multiparttosingleparts', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(40)
        if feedback.isCanceled():
            return {}

        # Extract by location WhiteOak
        alg_params = {
            'INPUT': outputs['MultipartToSinglepartsWhiteoak']['OUTPUT'],
            'INTERSECT': outputs['WhiteoakAcceptingMills']['OUTPUT'],
            'PREDICATE': [0],  # intersect
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByLocationWhiteoak'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(41)
        if feedback.isCanceled():
            return {}

        # Add Species Field WhiteOak
        alg_params = {
            'FIELD_LENGTH': 20,
            'FIELD_NAME': 'Species',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # String
            'FORMULA': "'WhiteOak'",
            'INPUT': outputs['ExtractByLocationWhiteoak']['OUTPUT'],
            'OUTPUT': parameters['WhiteOak']
        }
        outputs['AddSpeciesFieldWhiteoak'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['WhiteOak'] = outputs['AddSpeciesFieldWhiteoak']['OUTPUT']

        feedback.setCurrentStep(42)
        if feedback.isCanceled():
            return {}

        # WhitePine Accepting Mills
        alg_params = {
            'EXPRESSION': '"b.WhitePine" > 0',
            'INPUT': parameters['mills'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['WhitepineAcceptingMills'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(43)
        if feedback.isCanceled():
            return {}

        # WhitePine Isochrones
        alg_params = {
            'CELL_SIZE': 10000,
            'DEFAULT_DIRECTION': 2,  # Both directions
            'DEFAULT_SPEED': 5,
            'DIRECTION_FIELD': 'oneway',
            'ENTRY_COST_CALCULATION_METHOD': 0,  # Planar (only use with projected CRS)
            'ID_FIELD': 'new_id',
            'INPUT': parameters['roadnetwork'],
            'INTERVAL': 41842.94,
            'MAX_DIST': 127138.2,
            'SPEED_FIELD': '',
            'START_POINTS': outputs['WhitepineAcceptingMills']['OUTPUT'],
            'STRATEGY': 0,  # Shortest Path (distance optimization)
            'TOLERANCE': 0,
            'VALUE_BACKWARD': 'T',
            'VALUE_BOTH': 'B',
            'VALUE_FORWARD': 'F',
            'OUTPUT_INTERPOLATION': QgsProcessing.TEMPORARY_OUTPUT,
            'OUTPUT_POLYGONS': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['WhitepineIsochrones'] = processing.run('qneat3:isoareaaspolygonsfromlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(44)
        if feedback.isCanceled():
            return {}

        # Clip Landforms WhitePine
        alg_params = {
            'INPUT': outputs['WhitepineIsochrones']['OUTPUT_POLYGONS'],
            'OVERLAY': parameters['landforms'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ClipLandformsWhitepine'] = processing.run('native:clip', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(45)
        if feedback.isCanceled():
            return {}

        # Multipart to singleparts WhitePine
        alg_params = {
            'INPUT': outputs['ClipLandformsWhitepine']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MultipartToSinglepartsWhitepine'] = processing.run('native:multiparttosingleparts', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(46)
        if feedback.isCanceled():
            return {}

        # Extract by location WhitePine
        alg_params = {
            'INPUT': outputs['MultipartToSinglepartsWhitepine']['OUTPUT'],
            'INTERSECT': outputs['WhitepineAcceptingMills']['OUTPUT'],
            'PREDICATE': [0],  # intersect
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByLocationWhitepine'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(47)
        if feedback.isCanceled():
            return {}

        # Add Species Field WhitePine
        alg_params = {
            'FIELD_LENGTH': 20,
            'FIELD_NAME': 'Species',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # String
            'FORMULA': "'WhitePine'",
            'INPUT': outputs['ExtractByLocationWhitepine']['OUTPUT'],
            'OUTPUT': parameters['WhitePine']
        }
        outputs['AddSpeciesFieldWhitepine'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['WhitePine'] = outputs['AddSpeciesFieldWhitepine']['OUTPUT']
        return results

    def name(self):
        return 'Bolt Isochrones'

    def displayName(self):
        return 'Bolt Isochrones'

    def group(self):
        return 'Graduate School'

    def groupId(self):
        return 'Graduate School'

    def createInstance(self):
        return BoltIsochrones()

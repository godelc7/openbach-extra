from scenario_builder import Scenario
from scenario_builder.helpers.network.owamp import owamp_measure_owd
from scenario_builder.helpers.postprocessing.time_series import time_series_on_same_graph
from scenario_builder.helpers.postprocessing.histogram import cdf_on_same_graph, pdf_on_same_graph
from scenario_builder.openbach_functions import StartJobInstance, StartScenarioInstance


SCENARIO_DESCRIPTION="""This scenario allows to :
     - Launch the subscenario One Way Delay measurement for both directions
       (with owamp jobs).
     - Perform two postprocessing tasks to compare the
       time-series and the CDF of the one way delay measurements.
"""

def extract_jobs_to_postprocess(scenario):
    for function_id, function in enumerate(scenario.openbach_functions):
        if isinstance(function, StartJobInstance):
            if function.job_name == 'owamp-client':
                yield function_id


def one_way_delay(client, server, scenario_name='network_one_way_delay'):
    scenario = Scenario(scenario_name, 'OpenBACH Network One Way Delay Measurement')
    scenario.add_argument('ip_dst', 'Target of the pings and server IP adress')

    owamp_measure_owd(scenario, server, client, '$ip_dst')

    return scenario


def build(client, server, ip_dst, post_processing_entity, scenario_name):              
    scenario = Scenario(scenario_name, SCENARIO_DESCRIPTION)                                                                  
    
    one_way_delay_metrology = one_way_delay(client, server) 

    start_one_way_delay_metrology = scenario.add_function(                                                 
            'start_scenario_instance')                                                             
                                                                                                   
    start_one_way_delay_metrology.configure(                                                               
            one_way_delay_metrology,                                                                       
            ip_dst=ip_dst)                                                                         
                                                                                                   
    post_processed = [                                                                             
            [start_one_way_delay_metrology, function_id]                                                   
            for function_id in extract_jobs_to_postprocess(one_way_delay_metrology)                        
    ]                                                                                              
    
    time_series_on_same_graph(scenario, post_processing_entity, post_processed, [['owd_sent','owd_received']], [['One Way Delay (ms)']], [['One Way delays in both directions']], [start_one_way_delay_metrology], None, 2)
    cdf_on_same_graph(scenario, post_processing_entity, post_processed, 100, [['owd_sent', 'owd_received']], [['One Way Delay (ms)']], [['CDF of One Way delay in both directions']], [start_one_way_delay_metrology], None, 2)

    return scenario                                   

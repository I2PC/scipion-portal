delete from report_protocols_workflow 
where client_address IN (
'asimov-dos.cnb.csic.es',
'nolan.cnb.csic.es',
'cajal.cnb.csic.es',
'tumbao.cnb.csic.es',
'finlay.cnb.csic.es',
'turing.cnb.csic.es',
'oort.cnb.csic.es',
'einstein-dos.cnb.csic.es',
'carver.cnb.csic.es')

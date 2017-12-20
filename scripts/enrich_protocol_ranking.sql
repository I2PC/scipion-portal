/* Insert packages */
/* Clean package info */
update report_protocols_protocol set package_id = NULL;
delete from report_protocols_package;

insert into report_protocols_package (id, name) VALUES (1, 'Scipion');
update report_protocols_protocol set package_id = 1 where name like '%Import%' or name in 
	('ProtUnionSet','ProtPDFReport', 'ProtCTFAssign', 'ProtCreateMask', 'ProtMonitorSystem',
	'ProtAlignmentAssign','ProtSplitSet', 'ProtStress', 'ProtUserSubSet', 'ProtAverageFrames',
	'ProtCreateStreamData','LegacyProtocol','ProtSubSet','ProtMonitorCTF', 'ProtExtractCoords',
	'ProtMonitorSummary', 'ProtCreateFSC');

select * from report_protocols_protocol where name like '%Import%'

insert into report_protocols_package (id, name) VALUES (2, 'Xmipp');
update report_protocols_protocol set package_id = 2 where name like '%Xmipp%'
or name in ('BatchProtNMACluster', 'ProtMovieAssignGain', 'ChimeraProtRigidFit',
'ProtSubSetByMic');

insert into report_protocols_package (id, name) VALUES (3, 'Relion');
update report_protocols_protocol set package_id = 3 where name like '%Relion%';

insert into report_protocols_package (id, name) VALUES (4, 'Eman');
update report_protocols_protocol set package_id = 4 where name like '%Eman%' or
name in ('SparxGaussianProtPicking');

insert into report_protocols_package (id, name) VALUES (5, 'Spider');
update report_protocols_protocol set package_id = 5 where name like '%Spider%';

insert into report_protocols_package (id, name) VALUES (6, 'Motioncor/2');
update report_protocols_protocol set package_id = 6 where name like '%Motioncor%';

insert into report_protocols_package (id, name) VALUES (7, 'CTFfind');
update report_protocols_protocol set package_id = 7 where name like '%CTFFind%';

insert into report_protocols_package (id, name) VALUES (8, 'gCTF');
update report_protocols_protocol set package_id = 8 where name like '%Gctf%';

insert into report_protocols_package (id, name) VALUES (9, 'Freealign');
update report_protocols_protocol set package_id = 9 where name like '%Frealign%';

insert into report_protocols_package (id, name) VALUES (10, 'Not classified');
update report_protocols_protocol set package_id = 10 where name like '%Import%' or name in 
	('Prot3DFSC','CCP4ProtCoot', 'CCP4ProtRunRefmac', 'PowerfitProtRigidFit',
	 'ProtCryoEF','ProtLocScale','SpringProtSegmentExam','ProtSegmentHelices',
	 'AtsasProtConvertPdbToSAXS', 'ImagicProtMSA', 'ProtPrime');

insert into report_protocols_package (id, name) VALUES (11, 'Grigorieff lab');
update report_protocols_protocol set package_id = 11 where name like '%MagDis%' or name in 
	('ProtUnblur', 'ProtSummovie');

insert into report_protocols_package (id, name) VALUES (12, 'Bramford lab');
update report_protocols_protocol set package_id = 12 where name like '%ProtEthanPicker%';

insert into report_protocols_package (id, name) VALUES (13, 'BSOFT');
update report_protocols_protocol set package_id = 13 where name like '%Blocres%' or name in 
('BsoftProtParticlePicking');

insert into report_protocols_package (id, name) VALUES (14, 'Appion');
update report_protocols_protocol set package_id = 14 where name in 
('DogPickerProtPicking');

insert into report_protocols_package (id, name) VALUES (15, 'Emx');
update report_protocols_protocol set package_id = 15 where name in 
('ProtEmxExport');

insert into report_protocols_package (id, name) VALUES (16, 'Igbmc');
update report_protocols_protocol set package_id = 16 where name in 
('ProtGemPicker');

insert into report_protocols_package (id, name) VALUES (17, 'Opic');
update report_protocols_protocol set package_id = 17 where name in 
('ProtLocalizedExtraction');

insert into report_protocols_package (id, name) VALUES (18, 'DLS-Diamond Light Source');
update report_protocols_protocol set package_id = 18 where name in 
('ProtMonitorISPyB');

insert into report_protocols_package (id, name) VALUES (19, 'ESRF-European synchrotron');
update report_protocols_protocol set package_id = 19 where name in 
('ProtMonitorISPyB_ESRF');

insert into report_protocols_package (id, name) VALUES (20, 'Resmap');
update report_protocols_protocol set package_id = 20 where name in 
('ProtResMap');

insert into report_protocols_package (id, name) VALUES (21, 'Opic');
update report_protocols_protocol set package_id = 21 where name in 
('ProtLocalizedRecons');

insert into report_protocols_package (id, name) VALUES (22, 'Motioncor/2');
update report_protocols_protocol set package_id = 22 where name in 
('ProtMotionCorr');

insert into report_protocols_package (id, name) VALUES (23, 'Gautomatch');
update report_protocols_protocol set package_id = 23 where name in 
('ProtGautomatch');


select * from report_protocols_protocol where package_id is NULL;


/* Enrich types */
/* Clean types info */
update report_protocols_protocol set "protocolType_id" = NULL;
delete from report_protocols_protocoltype;
/**/
insert into report_protocols_protocoltype (id, name) VALUES (1, 'Movie alignment');
update report_protocols_protocol set "protocolType_id" = 1 where name in 
('ProtMotionCorr', 'ProtUnblur', 'ProtSummovie','XmippProtOFAlignment','XmippProtMovieAverage', 'XmippProtMovieCorr');

insert into report_protocols_protocoltype (id, name) VALUES (2, 'CTF estimation');
update report_protocols_protocol set "protocolType_id" = 2 where name in 
('XmippProtCTFMicrographs', 'ProtCTFFind', 'ProtGctf');

insert into report_protocols_protocoltype (id, name) VALUES (3, 'Initial model');
update report_protocols_protocol set "protocolType_id" = 3 where name in 
('XmippProtRansac', 'XmippProtReconstructSignificant', 'EmanProtInitModel');

insert into report_protocols_protocoltype (id, name) VALUES (4, 'Picking');
update report_protocols_protocol set "protocolType_id" = 4 where name in 
('BsoftProtParticlePicking','XmippProtParticlePickingPairs', 'SparxGaussianProtPicking', 'DogPickerProtPicking', 'XmippProtParticlePicking', 'XmippParticlePickingAutomatic');

insert into report_protocols_protocoltype (id, name) VALUES (5, '2D classification');
update report_protocols_protocol set "protocolType_id" = 5 where name in 
('XmippProtCL2D', 'ProtRelionClassify2D');

insert into report_protocols_protocoltype (id, name) VALUES (6, '3D refinement');
update report_protocols_protocol set "protocolType_id" = 6 where name in 
('ProtRelionRefine3D', 'XmippProtProjMatch', 'EmanProtRefine', 'ProtFreeAlign', 'SpiderProtRefinement', 'XmippProtReconstructHighRes');

select * from report_protocols_protocol where name like '%Refine%'

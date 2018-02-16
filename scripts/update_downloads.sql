update web_download set size = '207 MB', platform='Linux 64 bits' where platform = 'Linux 64 bits (207 MB)';
update web_download set size = '171 MB', platform='Linux 64 bits' where platform = 'Linux 64 bits (171 MB)';
update web_download set size = '26 MB', platform='Source code' where platform = 'Source code (26 MB)';
update web_download set size = '27 MB', platform='Source code' where platform = 'Source code (27 MB)';

select platform, size from web_download where size='10 MB';
select * from web_download 

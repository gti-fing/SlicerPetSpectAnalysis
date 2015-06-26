%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%   TACS GENERATION
% 
% Description: Scripts that generates a file 'TACs.mat' With the time
% activity curves.
%
% The script uses 
%    *functions: pTAC_feng.m , gentTACs.m
%    *files: EstadisticasTKM
% 
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

close all,clear all
addpath ../Files
addpath ../Functions

%Time definition.
To = 0;
Tend = 3600;
frameTime_eqspaced = To:1:Tend;

%pTAC definition
pTAChforsys = pTAC_feng(frameTime_eqspaced);
pTAChforsys = pTAChforsys*37000; %from nCi to Bq.

%tTAC curves
TKMParameters
[tTAC_grey,tTAC_white]=gentTACs(frameTime_eqspaced/60,pTAChforsys,Parameters_k);

%Sample frames
% (4 × 10, 4 × 60, 2 ×150, 2 × 300 and 4 × 600 s)
frameTime = [0,10,20,30,40,100,160,220,280,430,580,880,1180,1780,2380,2980,3580];
pTAC_s = zeros(1,length(frameTime)-1);
tTAC_grey_s = zeros(1,length(frameTime)-1);
tTAC_white_s = zeros(1,length(frameTime)-1);

for i=2:length(frameTime)
    Ind = (frameTime_eqspaced <= frameTime(i))&(frameTime_eqspaced >= frameTime(i-1));
    X = frameTime_eqspaced(Ind);
    Y = cumtrapz(X,pTAChforsys(Ind));
    pTAC_s(i) = Y(end)/(frameTime(i)-frameTime(i-1));
    
    Y = cumtrapz(X,tTAC_grey(Ind));
    tTAC_grey_s(i) = Y(end)/(frameTime(i)-frameTime(i-1));
    
    Y = cumtrapz(X,tTAC_white(Ind));
    tTAC_white_s(i) = Y(end)/(frameTime(i)-frameTime(i-1));  
end

%Plot
figure(),plot(frameTime,pTAC_s,'r*--'), hold on, plot(frameTime,tTAC_grey_s,'*--'),
plot(frameTime,tTAC_white_s,'k*--');

%Save
save('TACs.mat','frameTime','pTAC_s','tTAC_white_s','tTAC_grey_s'); 
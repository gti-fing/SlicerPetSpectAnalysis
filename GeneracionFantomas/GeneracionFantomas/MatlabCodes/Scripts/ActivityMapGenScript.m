%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%   Activity Map Generation Script
%   
% Generates the Activity Maps for each frame. The output files are in .yaff
% format, required by ASIM.
% Also generates the "lista_entrada.txt" that specifies the true number of
% counts to simulate for each frame.
%
% **Output files are stored in a folder called ActivityOutput
% 
% Uses the files: 
%   -TACs.mat: TACs Definitions 
%   -labelmapSimple_Les.bin: LabelMap
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

close all, clear all

%Load TACs.
load('TACs.mat','frameTime','pTAC_s','tTAC_white_s','tTAC_grey_s');
%Cerebral blood volume for white and grey matter
Vbw = 0.025;
Vbg = 0.045;
%Tumor consumption fraction
Tum = 0.2;
%TACs
tTAC_w = tTAC_white_s * (1-Vbw) + Vbw*pTAC_s;
tTAC_g = tTAC_grey_s * (1-Vbg) + Vbg*pTAC_s;
tTAC_t = tTAC_w*(1-Tum);

%Remove first zero activity
frameTime = frameTime(2:end);
tTAC_w = tTAC_w(2:end);
tTAC_g = tTAC_g(2:end);
tTAC_t = tTAC_t(2:end);
pTAC_s = pTAC_s(2:end);

%Plot
figure(),plot(frameTime,pTAC_s,'r*--'), hold on, plot(frameTime,tTAC_g,'*--'),
plot(frameTime,tTAC_w,'k*--'), plot(frameTime,tTAC_t,'g*--'), legend('pTAC', 'tTAC grey','tTAC white','tTAC tumor');

%Load MAP
fid=fopen('labelmapSimple_Les.bin','r');
MAP = fread(fid,'uint8');
fclose(fid);

%Dim & voxel_size
Dim = [181,217,181];
voxel_size = [1,1,1];
voxel_vol = voxel_size(1)*voxel_size(2)*voxel_size(3);

%Slice Show
MAP_r = reshape(MAP,Dim);
figure(),imshow(MAP_r(:,:,40)/max(MAP(:))),title('Label map');

%Set Activity Maps%
Activity = zeros(length(MAP),length(frameTime));
ASIM_activity = zeros(length(MAP),length(frameTime));
trues = zeros(1,length(frameTime));

%%%%%%%%% NOISE PARAMETERS%%%%%%%%
alfa = 5e-4;
G = 1000;
% Real alfa value is alfa/G (it is define this way to avoid overflow as we work with uint16)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


for  Fr = 1:length(frameTime)
      %Set activities
      ASIM_activity(MAP == 1,Fr) = tTAC_g(Fr); %Grey matter
      ASIM_activity(MAP == 2,Fr) = tTAC_w(Fr); %white matter
      ASIM_activity(MAP == 3,Fr) = pTAC_s(Fr); %Carotids
      ASIM_activity(MAP == 4,Fr) = tTAC_t(Fr); %tumors 
      ASIM_activity(MAP == 5,Fr) = tTAC_w(Fr); %scalp
      ASIM_activity(:,Fr) = ASIM_activity(:,Fr)/G;
      
      %Display image
      %im = reshape(ASIM_activity(:,Fr),Dim);
      %figure(),imshow(im(:,:,120)./max(im(:)));
      
      %Total Counts
      TotalCounts = sum(ASIM_activity(:,Fr));
      if Fr>1
        trues(Fr) = alfa*TotalCounts*(frameTime(Fr)-frameTime(Fr-1))*exp(-frameTime(Fr)/6586);
      else
        trues(Fr) = alfa*TotalCounts*(frameTime(1))*exp(-(frameTime(1))/6586);
      end
      
end

trues = round(trues)';

%SAVING ACTIVITY IMAGES: vascFantom_.yaff where _ is frame number
mkdir ActivityOutput


for i =1:length(frameTime)
    name = strcat('vascFantom',int2str(i),'.yaff');
    path = strcat('ActivityOutput',filesep,name);
    ASIM_activity_i = ASIM_activity(:,i);
    fid = fopen(path,'w');
    fwrite(fid,ASIM_activity_i,'uint16','b');
    fclose(fid);
end

%SAVING "TrueCounts_list.txt"
frame_number=1:length(frameTime);
frame_number=num2str(frame_number','%2.0f');
comas=','*ones(length(frame_number),1);
enters=char(10)*ones(length(frame_number),1);
nFot=int2str(trues);
string_list_file = 'TrueCounts_list';
string_list_path = strcat('ActivityOutput',filesep,string_list_file);
string_list=horzcat(frame_number,comas,nFot,enters)';
fid=fopen(string_list_path,'w');
fwrite(fid,string_list,'char');
fclose(fid);





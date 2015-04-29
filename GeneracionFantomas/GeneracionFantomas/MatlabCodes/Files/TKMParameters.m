%%Kintetic compartmental constants definitions for FDG.
%
%% Constants extracted from: 
%
%   Phelps ME, Huang SC, Hoffman EJ , Selin C, Sokoloff L , Kuhl DE
%   (1979) Tomographic measurements of local cerebral glucose metabolic
%   rate in humans with [F18]2-fluoro-2-deoxy-Dglucose: validation of
%   method. Ann Nellrol 6 : 3 7 1 - 388
%
%
%% K=k1*k3/(k2+k3)

Parameters_k=zeros(1,8); 

%Phelps GREY MATTER
Parameters_k(1)=0.102;
Parameters_k(2)=.130;
Parameters_k(3)=.062;
Parameters_k(4)=0.0068;


%%Phelps WHITE MATTER
Parameters_k(5)=0.054;
Parameters_k(6)=.109;
Parameters_k(7)=0.045;
Parameters_k(8)=0.0058;

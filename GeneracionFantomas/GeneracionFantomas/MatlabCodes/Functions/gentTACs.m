function [tTAC_grey,tTAC_white]=gentTACs(tiempo,pTAC,Parameters_k)

%Load kinetic constants
k1=Parameters_k(1,1);
k2=Parameters_k(1,2);
k3=Parameters_k(1,3);
k4=Parameters_k(1,4);

%Compartimental model linear system
a=[-(k2+k3) k4;k3 -k4];
b=[k1;0];
c=[1,1];
sys_grey=ss(a,b,c,0);


%Calculate output tTAC
[tTAC_grey]=lsim(sys_grey,pTAC,tiempo);

%Load kinetic constants
k1=Parameters_k(1,5);
k2=Parameters_k(1,6);
k3=Parameters_k(1,7);
k4=Parameters_k(1,8);

%Calculate output tTAC
a=[-(k2+k3) k4;k3 -k4];
b=[k1;0];
c=[1,1];
sys_white=ss(a,b,c,0);

[tTAC_white]=lsim(sys_white,pTAC,tiempo);
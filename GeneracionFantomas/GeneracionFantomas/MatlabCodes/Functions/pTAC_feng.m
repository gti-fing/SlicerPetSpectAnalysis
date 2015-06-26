%%Function that generates a pTAC curve using the formula and parameters%%
%
%Proposed in : 
%
%   Feng, D., Wang, X., & Yan, H. (1994). A computer simulation study
%   on the input function sampling schedules in tracer kinetic modeling
%   with positron emission tomography (PET). Computer methods and
%   programs in biomedicine, 45(3), 175-186.
%

function pTACh = pTAC_feng(t)
   %t : Time in seconds

   %Parameters
   b1=-4.1339;
   b2=-0.0104;
   b3=-0.1191;
   A2=21.8798;
   A1=851.1225;
   A3=20.8113;
   T = t/60;
   Tau = 0;
  
   pTACh= (A1*(T-Tau)-A2*ones(size(T))-A3*ones(size(T))).*exp(b1*(T-Tau))+ A2*exp(b2*(T-Tau))+ A3*exp(b3*(T-Tau));
   
   pTACh(T<Tau) = 0;
   
end

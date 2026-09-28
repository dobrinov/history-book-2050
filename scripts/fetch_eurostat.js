(async()=>{
const B='https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/';
const Q={
 gdp_pps:'prc_ppp_ind?geo=BG&geo=EU27_2020&na_item=VI_PPS_EU27_2020_HAB&ppp_cat=GDP',
 aic_pps:'prc_ppp_ind?geo=BG&na_item=VI_PPS_EU27_2020_HAB&ppp_cat=A01',
 price_level:'prc_ppp_ind?geo=BG&na_item=PLI_EU27_2020&ppp_cat=A01',
 gdp_growth:'tec00115?geo=BG',
 unemp:'une_rt_a?geo=BG&geo=EU27_2020&age=Y15-74&unit=PC_ACT&sex=T',
 hicp:'prc_hicp_aind?geo=BG&coicop=CP00&unit=RCH_A_AVG',
 minwage:'earn_mw_cur?geo=BG&currency=EUR',
 arope:'ilc_peps01n?geo=BG&geo=EU27_2020&age=TOTAL&sex=T&unit=PC',
 lifeexp:'demo_mlexpec?geo=BG&geo=EU27_2020&age=Y_LT1&sex=T&unit=YR',
 pop:'demo_pjan?geo=BG&age=TOTAL&sex=T',
 debt:'gov_10dd_edpt1?geo=BG&geo=EU27_2020&na_item=GD&sector=S13&unit=PC_GDP',
 deficit:'gov_10dd_edpt1?geo=BG&na_item=B9&sector=S13&unit=PC_GDP',
 infant:'demo_minfind?geo=BG&geo=EU27_2020&unit=RT',
 gini:'ilc_di12?geo=BG&geo=EU27_2020',
 earlyleave:'edat_lfse_14?geo=BG&sex=T&wstatus=POP&unit=PC',
 internet:'isoc_ci_in_h?geo=BG&hhtyp=TOTAL&indic_is=H_IACC&unit=PC_HH',
 emprate:'lfsi_emp_a?geo=BG&geo=EU27_2020&age=Y20-64&sex=T&indic_em=EMP_LFS&unit=PC_POP',
 smd:'ilc_mddd11?geo=BG&geo=EU27_2020&age=TOTAL&sex=T&unit=PC',
 roaddeaths:'tran_sf_roadus?geo=BG&unit=NR&pers_inj=KIL&tra_mode=TOTAL',
 emig:'migr_emi2?geo=BG&age=TOTAL&sex=T&agedef=REACH&citizen=TOTAL&unit=NR',
 netearn:'earn_nt_net?geo=BG&currency=EUR&estruct=NET&ecase=P1_NCH_AW100',
 fdi:'tec00046?geo=BG',
 arpr:'ilc_li02?geo=BG&age=TOTAL&sex=T&indic_il=LI_R_MD60&unit=PC',
 hhinc:'ilc_di03?geo=BG&age=TOTAL&sex=T&indic_il=MED_E&unit=EUR',
 hhinc_pps:'ilc_di03?geo=BG&geo=EU27_2020&age=TOTAL&sex=T&indic_il=MED_E&unit=PPS',
 tertiary:'edat_lfse_03?geo=BG&sex=T&age=Y30-34&isced11=ED5-8&unit=PC',
 fuelpov:'ilc_mdes01?geo=BG&geo=EU27_2020&hhtyp=TOTAL&incgrp=TOTAL&unit=PC',
};
const out={};
await Promise.all(Object.entries(Q).map(async([k,q])=>{
 try{const r=await fetch(B+q+'&format=JSON&lang=en');const j=await r.json();
  if(!j.dimension){out[k]='ERR '+JSON.stringify(j).slice(0,200);return;}
  const ids=j.id,size=j.size,res={};
  const cats=ids.map(d=>{const idx=j.dimension[d].category.index;const a=[];for(const c in idx)a[idx[c]]=c;return a;});
  for(const [flat,v] of Object.entries(j.value)){let n=+flat;const coord=[];for(let i=ids.length-1;i>=0;i--){coord[i]=cats[i][n%size[i]];n=Math.floor(n/size[i]);}
   const key=coord.filter((c,i)=>size[i]>1&&ids[i]!=='time').join('|')||'v';(res[key]=res[key]||{})[coord[ids.indexOf('time')]]=v;}
  out[k]=res;}catch(e){out[k]='ERR '+e;}
}));
return JSON.stringify(out);
})()

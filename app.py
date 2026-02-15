import streamlit as st
import streamlit.components.v1 as components
import base64

# [1] HTML 템플릿을 코드 최상단에 배치하여 들여쓰기 에러 원천 차단
HTML_TEMPLATE = """
<div style="position:relative; width:100%; background:#000; border-radius:10px; overflow:hidden;">
    <video id="v" controls style="width:100%;"></video>
    <canvas id="c" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none;"></canvas>
    <div id="m" style="position:absolute; top:10px; left:10px; background:rgba(255,0,0,0.8); color:#fff; padding:10px; font-family:monospace; border-radius:5px; font-weight:bold; display:none;">HYPER-RES (120fps)</div>
</div>
<script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
<script src="https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils"></script>
<script>
    const v=document.getElementById('v'), c=document.getElementById('c'), ctx=c.getContext('2d'), m=document.getElementById('m');
    let pL=null, pY=0;
    const pose=new Pose({locateFile:(f)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${f}`});
    pose.setOptions({modelComplexity:1, smoothLandmarks:true, minDetectionConfidence:0.5, minTrackingConfidence:0.5});
    pose.onResults((r)=>{
        if(!r.poseLandmarks) return;
        c.width=v.videoWidth; c.height=v.videoHeight;
        ctx.save(); ctx.clearRect(0,0,c.width,c.height);
        const w=r.poseLandmarks[15], h=r.poseLandmarks[23], vy=w.y-pY;
        if((vy>0.01 && w.y<h.y+0.2)||(w.y>=h.y-0.1 && w.y<=h.y+0.3)){
            m.style.display='block';
            if(pL){ [0.25,0.5,0.75].forEach(t=>{
                const mid=r.poseLandmarks.map((l,i)=>({x:pL[i].x+(l.x-pL[i].x)*t, y:pL[i].y+(l.y-pL[i].y)*t}));
                drawConnectors(ctx,mid,POSE_CONNECTIONS,{color:'rgba(0,255,255,0.4)',lineWidth:1});
            });}
        }else{m.style.display='none';}
        drawConnectors(ctx,r.poseLandmarks,POSE_CONNECTIONS,{color:'#00FF00',lineWidth:4});
        drawLandmarks(ctx,r.poseLandmarks,{color:'#FF0000',lineWidth:2,radius:5});
        pL=r.poseLandmarks; pY=w.y; ctx.restore();
    });
    v.src="VIDEO_SOURCE_HERE";
    async function run(){if(!v.paused&&!v.ended){await pose.send({image:v});}requestAnimationFrame(run);}
    v.onplay=run;
</script>
"""

st.set_page_config(layout="wide", page_title="GDR AI Final")

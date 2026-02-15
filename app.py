import streamlit as st
import streamlit.components.v1 as components
import base64

# [1] HTML 소스를 리스트 결합 방식으로 변경하여 따옴표 에러 원천 차단
# 파이썬이 줄바꿈을 혼동하지 않도록 한 줄씩 명확히 구분했습니다.
lines = [
    '<div id="w" style="width:100%;background:#000;border-radius:10px;overflow:hidden;position:relative;">',
    '    <video id="v" controls playsinline style="width:100%;display:block;"></video>',
    '    <canvas id="c" style="position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;"></canvas>',
    '    <div id="st" style="position:absolute;top:10px;left:10px;color:#fff;background:rgba(255,0,0,0.8);padding:8px;font-family:monospace;border-radius:5px;font-weight:bold;display:none;">HYPER-RES (120FPS+)</div>',
    '</div>',
    '<script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>',
    '<script src="https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils"></script>',
    '<script>',
    '    const v=document.getElementById("v"),c=document.getElementById("c"),ctx=c.getContext("2d"),st=document.getElementById("st");',
    '    let pL=null,pY=0;',
    '    const pose=new Pose({locateFile:(f)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${f}`});',
    '    pose.setOptions({modelComplexity:1,smoothLandmarks:true,minDetectionConfidence:0.5,minTrackingConfidence:0.5});',
    '    function lerp(a,b,t){return {x:a.x+(b.x-a.x)*t,y:a.y+(b.y-a.y)*t};}',
    '    pose.onResults((r)=>{',
    '        if(!r.poseLandmarks) return;',
    '        c.width=v.videoWidth; c.height=v.videoHeight;',
    '        ctx.save(); ctx.clearRect(0,0,c.width,c.height);',
    '        const w=r.poseLandmarks[15], h=r.poseLandmarks[23], vy=w.y-pY;',
    '        const isI = (vy>0.01 && w.y<h.y+0.2)||(w.y>=h.y-0.1 && w.y<=h.y+0.3);',
    '        if(isI && pL){',
    '            st.style.display="block";',
    '            [0.25,0.5,0.75].forEach(t=>{',
    '                const mid=r.poseLandmarks.map((l,i)=>lerp(pL[i],l,t));',
    '                drawConnectors(ctx,mid,POSE_CONNECTIONS,{color:"rgba(0,255,255,0.4)",lineWidth:1});',
    '            });',
    '        }else{st.style.display="none";}',
    '        drawConnectors(ctx,r.poseLandmarks,POSE_CONNECTIONS,{color:"#00FF00",lineWidth:4});',
    '        drawLandmarks(ctx,r.poseLandmarks,{color:"#FF0000",lineWidth:2,radius:5});',
    '        pL=r.poseLandmarks; pY=w.y; ctx.restore();',
    '    });',
    '    v.src="VIDEO

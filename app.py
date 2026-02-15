import streamlit as st
import streamlit.components.v1 as components
import base64

# [1] 하이퍼-레졸루션 엔진: 속도 기반 트리거 및 4배 보간 로직 포함
HTML_CODE = """
<div id="wrapper" style="width:100%; background:#000; border-radius:10px; overflow:hidden; position:relative;">
    <video id="v" controls playsinline style="width:100%; display:block;"></video>
    <canvas id="c" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none;"></canvas>
    <div id="st" style="position:absolute; top:10px; left:10px; color:#fff; background:rgba(0,123,255,0.8); padding:8px; font-family:monospace; border-radius:5px; z-index:100; font-weight:bold;">
        MODE: <span id="vfr">STANDARD</span>
    </div>
</div>
<script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
<script src="https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils"></script>
<script>
    const v = document.getElementById('v');
    const c = document.getElementById('c');
    const ctx = c.getContext('2d');
    const vfr = document.getElementById('vfr');

    let prevLM = null;
    let prevY = 0;

    const pose = new Pose({locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`});
    pose.setOptions({modelComplexity: 1, smoothLandmarks: true, minDetectionConfidence: 0.5, minTrackingConfidence: 0.5});

    // 프레임 사이를 메워주는 보간 함수
    function lerp(p1, p2, t) {
        return { x: p1.x + (p2.x - p1.x) * t, y: p1.y + (p2.y - p1.y) * t };
    }

    pose.onResults((r) => {
        if (!r.poseLandmarks) return;
        c.width = v.videoWidth; c.height = v.videoHeight;
        ctx.save(); ctx.clearRect(0, 0, c.width, c.height);
        
        const wrist = r.poseLandmarks[15];
        const hip = r.poseLandmarks[23];
        const vy = wrist.y - prevY; // 손목의 하강 속도 계산

        // [핵심] 다운스윙 및 임팩트 구간 트리거 (속도 0.01 이상 및 특정 높이)
        const isImpact = (vy > 0.01 && wrist.y < hip.y + 0.15) || (wrist.y > hip.y - 0.1 && wrist.y < hip.y +

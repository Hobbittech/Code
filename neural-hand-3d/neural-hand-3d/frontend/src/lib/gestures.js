export const GESTURES = [
  ["open_palm", "Open Palm", "Neutral/reset gesture"],
  ["fist", "Fist", "Select / grab"],
  ["point", "Point", "Rotate / target"],
  ["thumbs_up", "Thumbs Up", "Confirm"],
  ["thumbs_down", "Thumbs Down", "Reject"],
  ["peace", "Peace", "Change mode"],
  ["pinch", "Pinch", "Interact"],
  ["two_finger", "Two Finger", "Secondary interaction"],
  ["three_finger", "Three Finger", "Scale up"],
  ["four_finger", "Four Finger", "Alternate mode"]
];

const dist = (a, b) => Math.hypot(a.x-b.x, a.y-b.y, a.z-b.z);
const angle = (a,b,c) => {
  const ab={x:a.x-b.x,y:a.y-b.y,z:a.z-b.z}, cb={x:c.x-b.x,y:c.y-b.y,z:c.z-b.z};
  const dot=ab.x*cb.x+ab.y*cb.y+ab.z*cb.z;
  const mag=Math.hypot(ab.x,ab.y,ab.z)*Math.hypot(cb.x,cb.y,cb.z);
  return mag ? Math.acos(Math.max(-1,Math.min(1,dot/mag))) : 0;
};

export function classifyGesture(lm) {
  if (!lm || lm.length < 21) return { name:"unknown", confidence:0 };
  const tips=[8,12,16,20], pips=[6,10,14,18];
  const extended=tips.map((t,i)=>dist(lm[t],lm[0]) > dist(lm[pips[i]],lm[0])*1.12);
  const count=extended.filter(Boolean).length;
  const pinch=dist(lm[4],lm[8]) < 0.055;
  const thumbUp=lm[4].y < lm[3].y && !extended.slice(1).some(Boolean);
  const thumbDown=lm[4].y > lm[3].y && !extended.slice(1).some(Boolean);
  if (pinch) return {name:"pinch", confidence:.92};
  if (thumbUp) return {name:"thumbs_up", confidence:.86};
  if (thumbDown) return {name:"thumbs_down", confidence:.84};
  if (count===0) return {name:"fist", confidence:.9};
  if (count===1 && extended[0]) return {name:"point", confidence:.86};
  if (count===2 && extended[0] && extended[1]) {
    const spread=dist(lm[8],lm[12]);
    return {name:spread>.09?"peace":"two_finger", confidence:.82};
  }
  if (count===3) return {name:"three_finger", confidence:.8};
  if (count===4) return {name:"four_finger", confidence:.8};
  if (count>=4 && angle(lm[5],lm[9],lm[13])>1.2) return {name:"open_palm", confidence:.78};
  return {name:"open_palm", confidence:.65};
}

export function gestureAction(gesture) {
  const actions = {
    open_palm:{type:"reset"},
    fist:{type:"select"},
    pinch:{type:"interact"},
    point:{type:"rotate"},
    thumbs_up:{type:"confirm"},
    peace:{type:"mode"},
    three_finger:{type:"scale_up"}
  };
  return actions[gesture]?.type || null;
}

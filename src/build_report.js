const fs=require('fs'), path=require('path');
const D=require('docx');
const {Tab,TabStopType,TabStopPosition,PositionalTab,PositionalTabAlignment,PositionalTabRelativeTo,PositionalTabLeader,Document,Packer,Paragraph,TextRun,ImageRun,Table,TableRow,TableCell,WidthType,ShadingType,AlignmentType,HeadingLevel,PageBreak,Footer,PageNumber,TableOfContents,BorderStyle,LevelFormat,VerticalAlign}=D;
const P='/home/claude/de_tai_2/'; const FONT='Times New Roman';
const W=9071; // A4 content width (left 3cm, right 2cm)
function runs(t,base={}){ // **bold**, `code`, [placeholder]
  const out=[]; const re=/(\*\*[^*]+\*\*|`[^`]+`|\[[^\]]*\])/g; let last=0,m;
  while((m=re.exec(t))){ if(m.index>last) out.push(new TextRun({text:t.slice(last,m.index),font:FONT,...base}));
    const tok=m[0];
    if(tok.startsWith('**')) out.push(new TextRun({text:tok.slice(2,-2),bold:true,font:FONT,...base}));
    else if(tok.startsWith('`')) out.push(new TextRun({text:tok.slice(1,-1),font:'Consolas',...base,size:(base.size||26)-2}));
    else out.push(new TextRun({text:tok,font:FONT,...(/^\[(\d|Fact)/.test(tok)?{}:{highlight:'yellow'}),...base}));
    last=m.index+tok.length;}
  if(last<t.length) out.push(new TextRun({text:t.slice(last),font:FONT,...base}));
  return out;}
const body=(t,o={})=>new Paragraph({children:runs(t,{size:26}),spacing:{line:360,after:100},alignment:AlignmentType.JUSTIFIED,...o});
function pngSize(f){const b=fs.readFileSync(f);return [b.readUInt32BE(16),b.readUInt32BE(20)];}
const figs=[],tabs=[];
function parse(md){
  const lines=md.split('\n'); const blocks=[]; let i=0;
  while(i<lines.length){ const l=lines[i];
    if(!l.trim()){i++;continue;}
    if(l.startsWith('# ')) blocks.push({t:'h1',x:l.slice(2)});
    else if(l.startsWith('## ')) blocks.push({t:'h2',x:l.slice(3)});
    else if(l.startsWith('### ')) blocks.push({t:'h3',x:l.slice(4)});
    else if(l.startsWith('![')){const m=l.match(/!\[(.*)\]\((.*)\)/); figs.push(m[1]); blocks.push({t:'img',cap:m[1],f:m[2]});}
    else if(l.startsWith('|')){const rows=[]; while(i<lines.length&&lines[i].startsWith('|')){ if(!/^\|[-| ]+\|$/.test(lines[i])) rows.push(lines[i].split('|').slice(1,-1).map(s=>s.trim())); i++;} blocks.push({t:'tbl',rows}); continue;}
    else if(/^\*\*Bảng [^*]+\*\*$/.test(l.trim())){tabs.push(l.trim().slice(2,-2)); blocks.push({t:'tcap',x:l.trim().slice(2,-2)});}
    else if(/^- /.test(l)) blocks.push({t:'li',x:l.slice(2)});
    else if(/^\d+\. /.test(l)) blocks.push({t:'ol',x:l.replace(/^\d+\. /,''),n:l.match(/^\d+/)[0]});
    else blocks.push({t:'p',x:l});
    i++;}
  return blocks;}
const chapters=['c1','c2','c3','c4','c5'].map(n=>parse(fs.readFileSync(P+`report/final/${n}.md`,'utf8')));
function render(blocks){
  const out=[]; let first=true;
  for(const b of blocks){
    if(b.t==='h1'){out.push(new Paragraph({heading:HeadingLevel.HEADING_1,pageBreakBefore:true,children:[new TextRun({text:b.x,font:FONT,bold:true,size:30})],alignment:AlignmentType.CENTER,spacing:{after:240}}));}
    else if(b.t==='h2') out.push(new Paragraph({heading:HeadingLevel.HEADING_2,children:[new TextRun({text:b.x,font:FONT,bold:true,size:28})],spacing:{before:200,after:120}}));
    else if(b.t==='h3') out.push(new Paragraph({heading:HeadingLevel.HEADING_3,children:[new TextRun({text:b.x,font:FONT,bold:true,italics:true,size:26})],spacing:{before:160,after:100}}));
    else if(b.t==='p') out.push(body(b.x));
    else if(b.t==='li') out.push(new Paragraph({numbering:{reference:'bul',level:0},children:runs(b.x,{size:26}),spacing:{line:360,after:60},alignment:AlignmentType.JUSTIFIED}));
    else if(b.t==='ol') out.push(new Paragraph({children:runs(b.n+'. '+b.x,{size:26}),indent:{left:360},spacing:{line:360,after:60},alignment:AlignmentType.JUSTIFIED}));
    else if(b.t==='tcap') out.push(new Paragraph({keepNext:true,alignment:AlignmentType.CENTER,spacing:{before:160,after:80},children:[new TextRun({text:b.x,font:FONT,bold:true,size:24})]}));
    else if(b.t==='img'){const f=P+'figures/'+b.f; const [w,h]=pngSize(f); const mw=15.5*37.8*1, sc=Math.min(1,(W/15*0.0+ 560)/w); const wp=Math.min(560,w*0.38*1), hp=wp*h/w;
      out.push(new Paragraph({keepNext:true,alignment:AlignmentType.CENTER,spacing:{before:120,after:60},children:[new ImageRun({type:'png',data:fs.readFileSync(f),transformation:{width:wp,height:hp},altText:{title:b.cap,description:b.cap,name:b.f}})]}));
      out.push(new Paragraph({alignment:AlignmentType.CENTER,spacing:{after:200},children:[new TextRun({text:b.cap,font:FONT,italics:true,size:24})]}));}
    else if(b.t==='tbl'){const n=b.rows[0].length; const lens=b.rows.reduce((a,r)=>r.map((c,j)=>Math.max(a[j]||0,Math.min(c.length,40))),[]);
      const tot=lens.reduce((a,c)=>a+Math.max(c,9),0); let cw=lens.map(c=>Math.floor(W*Math.max(c,9)/tot)); cw[n-1]+=W-cw.reduce((a,c)=>a+c,0);
      const bd={style:BorderStyle.SINGLE,size:4,color:'808080'}; const borders={top:bd,bottom:bd,left:bd,right:bd};
      out.push(new Table({width:{size:W,type:WidthType.DXA},columnWidths:cw,rows:b.rows.map((r,ri)=>new TableRow({tableHeader:ri===0,cantSplit:true,children:r.map((c,j)=>new TableCell({borders,width:{size:cw[j],type:WidthType.DXA},verticalAlign:VerticalAlign.CENTER,margins:{top:50,bottom:50,left:80,right:80},shading:ri===0?{fill:'D9E2F3',type:ShadingType.CLEAR,color:'auto'}:undefined,children:[new Paragraph({alignment:ri===0?AlignmentType.CENTER:AlignmentType.LEFT,children:runs(c,{size:22,bold:ri===0})})]}))}))}));
      out.push(new Paragraph({spacing:{after:160},children:[]}));}
  } return out;}
let PG={}; try{PG=JSON.parse(fs.readFileSync('/home/claude/build/pages.json','utf8'));}catch(e){}
const entry=(t,lvl=0)=>new Paragraph({spacing:{line:300,after:50},indent:{left:lvl*400},tabStops:[{type:TabStopType.RIGHT,position:W,leader:'dot'}],children:[new TextRun({text:t,font:FONT,size:26}),new TextRun({children:[new Tab(),String(PG[t]||'')],font:FONT,size:26})]});
const heads=chapters.flat().filter(b=>b.t==='h1'||b.t==='h2').map(b=>({x:b.x,l:b.t==='h1'?0:1}));
const chapterParas=chapters.flatMap(render);
// ---- front matter
const ctr=(t,o={})=>new Paragraph({alignment:AlignmentType.CENTER,spacing:{after:o.after??120},children:[new TextRun({text:t,font:FONT,size:o.size||26,bold:o.bold,highlight:o.hl?'yellow':undefined})]});
const cover=[ctr('[TÊN TRƯỜNG / KHOA]',{bold:true,hl:true,after:60}),ctr('BÁO CÁO TIỂU LUẬN HỌC PHẦN LẬP TRÌNH PYTHON',{bold:true,size:28,after:60}),ctr('Học kỳ 1, năm học 2026-2027, lớp học phần 020100138002',{after:900}),
 ctr('ĐỀ TÀI 2',{bold:true,size:32,after:120}),ctr('PHÂN TÍCH DỮ LIỆU Y TẾ VÀ XÂY DỰNG ỨNG DỤNG HỖ TRỢ DỰ ĐOÁN NGUY CƠ MẮC BỆNH TIM MẠCH',{bold:true,size:32,after:900}),
 ctr('Giảng viên: [Họ tên giảng viên]',{hl:true}),ctr('Sinh viên thực hiện: [Họ và tên]',{hl:true}),ctr('MSSV: [MSSV]    STT: [STT]',{hl:true}),ctr('Link dự án: [URL GitHub/GitLab]',{hl:true,after:900}),ctr('[Địa danh], tháng 11 năm 2026',{hl:true})];
const hd=t=>new Paragraph({pageBreakBefore:true,alignment:AlignmentType.CENTER,spacing:{after:240},children:[new TextRun({text:t,font:FONT,bold:true,size:30})]});
const lst=a=>a.map(x=>new Paragraph({spacing:{line:300,after:60},children:[new TextRun({text:x,font:FONT,size:26})]}));
const abbr=[['AI','Artificial Intelligence (trí tuệ nhân tạo)'],['AUC','Area Under the Curve'],['CSV','Comma-Separated Values'],['CV','Cross-validation (kiểm định chéo)'],['EDA','Exploratory Data Analysis (phân tích khám phá dữ liệu)'],['IQR','Interquartile Range (khoảng tứ phân vị)'],['ROC','Receiver Operating Characteristic'],['SMOTE','Synthetic Minority Over-sampling Technique'],['UCI','University of California, Irvine'],['WHO','World Health Organization (Tổ chức Y tế Thế giới)'],['CVD','Cardiovascular disease (bệnh tim mạch)']];
const abbrTbl=new Table({width:{size:W,type:WidthType.DXA},columnWidths:[2000,W-2000],rows:abbr.map(r=>new TableRow({children:r.map((c,j)=>new TableCell({width:{size:j?W-2000:2000,type:WidthType.DXA},borders:{top:{style:BorderStyle.NONE},bottom:{style:BorderStyle.NONE},left:{style:BorderStyle.NONE},right:{style:BorderStyle.NONE}},margins:{top:40,bottom:40,left:80,right:80},children:[new Paragraph({children:[new TextRun({text:c,font:FONT,size:26,bold:j===0})]})]}))}))});
const phancong=[hd('BẢNG PHÂN CÔNG VÀ TỶ LỆ ĐÓNG GÓP'),new Paragraph({alignment:AlignmentType.CENTER,spacing:{before:120,after:80},children:[new TextRun({text:'Bảng phân công công việc và tỷ lệ đóng góp của các thành viên',font:FONT,bold:true,size:24})]}),
 new Table({width:{size:W,type:WidthType.DXA},columnWidths:[600,2300,1300,3571,1300],rows:[['STT','Họ và tên','MSSV','Công việc phụ trách','Đóng góp (%)'],['1','[ ]','[ ]','[ ]','[ ]'],['2','[ ]','[ ]','[ ]','[ ]'],['','Tổng','','','100']].map((r,ri)=>new TableRow({children:r.map((c,j)=>new TableCell({width:{size:[600,2300,1300,3571,1300][j],type:WidthType.DXA},borders:{top:{style:BorderStyle.SINGLE,size:4,color:'808080'},bottom:{style:BorderStyle.SINGLE,size:4,color:'808080'},left:{style:BorderStyle.SINGLE,size:4,color:'808080'},right:{style:BorderStyle.SINGLE,size:4,color:'808080'}},margins:{top:60,bottom:60,left:80,right:80},shading:ri===0?{fill:'D9E2F3',type:ShadingType.CLEAR,color:'auto'}:undefined,children:[new Paragraph({children:[new TextRun({text:c,font:FONT,size:24,bold:ri===0,highlight:c==='[ ]'?'yellow':undefined})]})]}))}))}),
 new Paragraph({spacing:{before:120},children:[new TextRun({text:'Điền thông tin thực tế trước khi nộp.',font:FONT,italics:true,size:22})]})];
const refs=['World Health Organization. (n.d.). Cardiovascular diseases (CVDs) [Fact sheet]. https://www.who.int/news-room/fact-sheets/detail/cardiovascular-diseases-(cvds) [ngày truy cập]','Detrano, R., Janosi, A., Steinbrunn, W., Pfisterer, M., Schmid, J.-J., Sandhu, S., Guppy, K. H., Lee, S., & Froelicher, V. (1989). International application of a new probability algorithm for the diagnosis of coronary artery disease. The American Journal of Cardiology, 64(5), 304–310.','Dua, D., & Graff, C. (2019). UCI Machine Learning Repository. University of California, Irvine. https://archive.ics.uci.edu','Pedregosa, F., et al. (2011). Scikit-learn: Machine learning in Python. Journal of Machine Learning Research, 12, 2825–2830.','Chawla, N. V., Bowyer, K. W., Hall, L. O., & Kegelmeyer, W. P. (2002). SMOTE: Synthetic minority over-sampling technique. Journal of Artificial Intelligence Research, 16, 321–357.'];
const refParas=[hd('TÀI LIỆU THAM KHẢO'),...refs.map(r=>new Paragraph({indent:{left:567,hanging:567},spacing:{line:360,after:100},children:runs(r,{size:26})}))];
const doc=new Document({
 styles:{default:{document:{run:{font:FONT,size:26}}},paragraphStyles:[
  {id:'Heading1',name:'Heading 1',basedOn:'Normal',next:'Normal',quickFormat:true,run:{font:FONT,size:30,bold:true,color:'000000'},paragraph:{spacing:{before:240,after:240},outlineLevel:0}},
  {id:'Heading2',name:'Heading 2',basedOn:'Normal',next:'Normal',quickFormat:true,run:{font:FONT,size:28,bold:true,color:'000000'},paragraph:{spacing:{before:200,after:120},outlineLevel:1}},
  {id:'Heading3',name:'Heading 3',basedOn:'Normal',next:'Normal',quickFormat:true,run:{font:FONT,size:26,bold:true,italics:true,color:'000000'},paragraph:{spacing:{before:160,after:100},outlineLevel:2}}]},
 numbering:{config:[{reference:'bul',levels:[{level:0,format:LevelFormat.BULLET,text:'•',alignment:AlignmentType.LEFT,style:{paragraph:{indent:{left:720,hanging:360}}}}]}]},
 sections:[{properties:{page:{size:{width:11906,height:16838},margin:{top:1134,bottom:1134,left:1701,right:1134}}},
  footers:{default:new Footer({children:[new Paragraph({alignment:AlignmentType.CENTER,children:[new TextRun({children:[PageNumber.CURRENT],font:FONT,size:24})]})]})},
  children:[...cover,
   hd('MỤC LỤC'),...heads.map(h=>entry(h.x,h.l)),...['DANH MỤC HÌNH','DANH MỤC BẢNG','DANH MỤC TỪ VIẾT TẮT','BẢNG PHÂN CÔNG VÀ TỶ LỆ ĐÓNG GÓP','TÀI LIỆU THAM KHẢO'].map(t=>entry(t)),
   hd('DANH MỤC HÌNH'),...figs.map(f=>entry(f)),hd('DANH MỤC BẢNG'),...tabs.concat(['Bảng phân công công việc và tỷ lệ đóng góp của các thành viên']).map(f=>entry(f)),
   hd('DANH MỤC TỪ VIẾT TẮT'),abbrTbl,...phancong,...chapterParas,...refParas]}]});
Packer.toBuffer(doc).then(b=>{fs.writeFileSync('/home/claude/build/bao_cao.docx',b);console.log('ok',figs.length,'hinh',tabs.length,'bang');});

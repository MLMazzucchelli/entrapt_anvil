from anvil import *
import anvil.js
from anvil.js.window import document

class Loading:
    def __init__(self,text=''):
        self.text=text
        
    def __enter__(self):
        html=f"""
<div class="bar-container">
    <div class="progress-bar">
        <div class="progress-bar-value"></div>
    </div>
    <center class='loading-prompt'>{self.text}</center>
</div>
<style>
.bar-container {{
  width: 100vw;
  height: 100vh;
  margin: 0px;
  position: fixed;
  top: 0px;
  
  z-index: 999999999;
  background-color: rgba(0,0,0,0.6);
}}

.progress-bar {{
  height: 6.5px;
  background: #002440;
  background-image: none;
  width: 100%;
  overflow: hidden;
}}

.progress-bar-value {{
  width: 100%;
  height: 100%;
  background-color: #15f4ee;
  animation: indeterminateAnimation 1.5s infinite linear;
  transform-origin: 0% 50%;
}}

.loading-prompt {{
  margin-top: 8px;
  padding: 10px 20px;
  background: #002440;
  position: relative;
  left: 50%; 
  color: white;
  transform: translateX(-50%);
  display:inline-block;
  font-size: 18px;
  border-radius: 10px;
}}

@keyframes indeterminateAnimation {{
  0% {{
    transform:  translateX(0) scaleX(0);
  }}
  40% {{
    transform:  translateX(0) scaleX(0.4);
  }}
  100% {{
    transform:  translateX(100%) scaleX(0.5);
  }}
}}
        """
        template=HtmlTemplate(html=html)
        self.loading_system=anvil.js.get_dom_node(template)
        document.body.appendChild(self.loading_system)
    
    def __exit__(self, *args, **kwargs):
        self.loading_system.remove()
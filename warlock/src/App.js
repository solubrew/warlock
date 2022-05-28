//@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
/*---  #																																				||
<(META)>:  #																																		||
	DOCid: #								||
	name: #														||
	description: >  #																															||
	expirary: <[expiration]>  #																										||
	version: <[version]>  #																												||
	path: <[LEXIvrs]>  #																													||
	outline: <[outline]>  #																												||
	authority: document|this  #																										||
	security: sec|lvl2  #																													||
	<(WT)>: -32  #																																||
# -*- coding: utf-8 -*-#																												*/
//================================Core Modules==================================||
import React, { useState, useEffect } from 'react';//														||
import logo from './logo.svg';//																								||
import './App.css';//																														||
//==============================================================================||
/*App */
function App() {//																															||
	const [currentTime, setCurrentTime] = useState(0);//													||
  useEffect(() => {fetch('/time').then(res => res.json()).then(data => {//			||
      																		setCurrentTime(data.time);});}, []);//||
  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>Edit <code>src/App.js</code> and save to reload.</p>
        <a className="App-link" href="https://reactjs.org" target="_blank"
																		rel="noopener noreferrer">Learn React</a>
        <p>The current time is {currentTime}.</p>
      </header>
    </div>
  );}//																																					||
export default App;//																														||
/*==============================================================================||
https://blog.miguelgrinberg.com/post/how-to-create-a-react--flask-project
================================================================================*/

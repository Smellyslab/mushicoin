import React, { Component } from 'react';
import axios from 'axios';
import WalletManagement from './WalletManagement.js';
import Mining from './Mining.js';
import AppBar from 'material-ui/AppBar';
import Drawer from 'material-ui/Drawer';
import MenuItem from 'material-ui/MenuItem';
import Home from 'material-ui/svg-icons/action/home';
import Settings from 'material-ui/svg-icons/action/settings';
import Lock from 'material-ui/svg-icons/action/lock';
import Blockcount from './widgets/blockcount.js';

class MainPage extends Component {

  constructor(props){
    super(props);
    this.state = {
      'default_wallet': null,
      'drawer_open': false,
      'page': 'main'
    }
  }

  componentDidMount() {
    this.getDefaultWallet();
  }

  drawerToggle = () => this.setState((state) => {
    state.drawer_open = !state.drawer_open;
    return state;
  });

  changePage = (newPage) => {
    this.setState({
      page: newPage,
      drawer_open: false
    })
  }

  getDefaultWallet = () => {
    axios.get("/info_wallet").then((response) => {
      let data = response.data;
      if(data.hasOwnProperty('address')) {
        this.setState({default_wallet:data});
      }
      else {
        this.setState({default_wallet:null});
      }
    });
  }

  onLogout = () => {
    let data = new FormData()
    data.append('delete', true);

    axios.post('/set_default_wallet', data).then((response) => {
      
    }).catch((error) => {
      this.props.notify('Failed to logout', 'error');
    })
  }

  render() {
    let currentPage = <div />
    if(this.state.page === 'main') {
      currentPage = <WalletManagement notify={this.props.notify} default_wallet={this.state.default_wallet} />;
    }
    else if(this.state.page === 'mining') {
      currentPage = <Mining notify={this.props.notify} default_wallet={this.state.default_wallet} />
    }
    return (
      <div>
        <AppBar
          title="Coinami"
          iconClassNameRight="muidocs-icon-navigation-expand-more"
          onLeftIconButtonClick={this.drawerToggle}
        />
        <Drawer open={this.state.drawer_open} docked={false} onRequestChange={(drawer_open) => this.setState({drawer_open})}>
          <MenuItem leftIcon={<Home />} onClick={() => {this.changePage('main')}} >Home</MenuItem>
          <MenuItem leftIcon={<Settings />} onClick={() => {this.changePage('mining')}}>Mining</MenuItem>
          <MenuItem leftIcon={<Lock />} onClick={this.onLogout}>Logout</MenuItem>
        </Drawer>
        {currentPage}
        <Blockcount />
      </div>
    );
  }
}

export default MainPage;

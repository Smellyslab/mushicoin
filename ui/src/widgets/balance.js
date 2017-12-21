import React, { Component } from 'react';
import {MCardStats} from '../components/card.js';

class Balance extends Component {

  render() {
    let balance = 0;
    let name = "";
    if(this.props.wallet !== null){
      balance = this.props.wallet.balance;
      name = this.props.wallet.name;
    }
    return (       
      <div className="col-lg-6 col-md-12 col-sm-12">
        <MCardStats color="green" header_icon="trending_up" title="Balance"
         content={balance}
         footer_icon="local_offer" alt_text={"Belongs to: " + name}/>
      </div>
    );
  }
}

export default Balance;
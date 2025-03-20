// SPDX-License-Identifier: UNLICENSED
//ipfs repo gc
//Need to write code to clear the mappings as well
pragma solidity ^0.8.13;

contract Sairam 
{
    mapping(uint8 => string) public expert_public_key;
    mapping(uint8 => string) public partition_cid;
    mapping(uint8 => string) public predictions;
    mapping(uint8 => int) public reputation;
    uint public counter;
    uint public MAXEXPERTS;
    uint public NUMROUNDS;
    bool public calculated;//NEed to add these in Constructor

    constructor(uint _MAXEXPERTS,uint _NUMROUDS)
    {
        MAXEXPERTS = _MAXEXPERTS;
        NUMROUNDS = _NUMROUDS;
        calculated = false;
        counter = 0;
    }

    function setup(uint8 _level,uint8 _number,uint _MAXEXPERTS,uint _NUMROUDS) public
    {
        // Not Everyone should Access It
        // 0 Stands for complete wipe 
        // Predictions -> 0...N,N+1,N+2
        // Partition_CID -> 0..N
        // Expert_Public_Key -> 0...N
        MAXEXPERTS = _MAXEXPERTS;
        NUMROUNDS = _NUMROUDS;
        counter = 0;
        //Basically Resets Everything exclusievly for repeated executions
        if(_level == 0)
        {
            //Clearing Expert Public Key
            for(uint8 i = 0;i<_number;i++)
            {
                delete expert_public_key[i];
            }
        }
        //Clearing Partition CID
        for(uint8 i = 0;i<_number;i++)
            {
                delete partition_cid[i];
                delete predictions[i];
            }
        delete predictions[_number+1];
        delete predictions[_number+2];//Keep Attention Here as well
    }

    function updatePartition(uint8 _number, string memory _str) public
    {
        partition_cid[_number] = _str;
    }
    function updateExpertPublicKey(uint8 _number, string memory _str) public
    {
        expert_public_key[_number] = _str;
    }
    function updatePredictions(uint8 _number, string memory _str) public
    {
        predictions[_number] = _str;
        counter = counter+1;
        //Write code such that once all predictions are set it should call calculate trust
    }
    function calculateTrust() public
    {
        bytes memory base = bytes(predictions[uint8(MAXEXPERTS)]);
        bytes memory consensus = bytes(predictions[uint8(MAXEXPERTS+1)]);
        bytes memory temp = "COM";
        int score = 0;
        for(uint8 i = 0;i<MAXEXPERTS;i++)
        {
            temp = bytes(predictions[i]);//Prediction of one Expert
            score = 0;
            for(uint8 j = 0;j<NUMROUNDS;j++)
            {   
                
                if(base[j] == consensus[j] && temp[j] != consensus[j])
                {//Individual Performance of the model is bad, but because of Consensus
                //It is working fine
                    if(score > 11)
                        {score = score-10;}
                    else
                        {score = 1;}
                }
                if(base[j] == temp[j] && base[j] == consensus[j])
                {//Ideal Situation Where All theree are same
                    score = score+10;
                }
               
                if(base[j] == temp[j] && base[j] != consensus[j])
                {//Individual Prediction of Model is good,but all the other models messed up
                    score = score+10;
                }
                if(base[j] != consensus[j])
                {//All the models messed up
                    if(score>6)
                    {score = score-5;}
                    else
                    {score = 1;}
                }

            }

            reputation[i] = score;
        }
        calculated = true;
    }
    function calculateBackUpTrust() public
    {
        bytes memory base = bytes(predictions[uint8(MAXEXPERTS)]);
        bytes memory temp = "COM";
        int score = 0;
        for(uint8 i = 0;i<MAXEXPERTS;i++)
        {
            temp = bytes(predictions[i]);//Prediction of one Expert
            score = 0;
            for(uint8 j = 0;j<NUMROUNDS;j++)
            {
                if(base[j] == temp[j])
                {//Ideal Situation Ground Truth is same as Predicted
                    score = score+10;
                }

                if(base[j] != temp[j])
                {//Individual Prediction of Model is not same as ground truth
                    if(score > 10)
                    {score = score-10;}
                    else
                    {score = 1;}
                }


            }

            reputation[i] = score;
        }
        calculated = true;
    }

    
}

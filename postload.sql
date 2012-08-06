update fec_indiv set amount=amount*-1 where transaction_type = '22Y' and amount>0;
update fec_pac2cand set amount=amount*-1 where transaction_type = '22Z' and amount>0;
update fec_pac2pac set amount=amount*-1 where transaction_type = '22Z' and amount>0;








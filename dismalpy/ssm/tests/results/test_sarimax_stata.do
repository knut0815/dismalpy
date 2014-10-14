// Example 1: ARIMA model
use http://www.stata-press.com/data/r12/wpi1, clear
arima wpi, arima(1,1,1)
arima wpi, arima(1,1,1) diffuse

// Estimate an AR(3) via a state-space model
// (to test prediction, standardized residuals, predicted states 
constraint 1 [D.wpi]u1 = 1
constraint 2 [u2]L.u1 = 1
constraint 3 [u3]L.u2 = 1

sspace (u1 L.u1 L.u2 L.u3, state noconstant) ///
       (u2 L.u1, state noconstant noerror) ///
       (u3 L.u2, state noconstant noerror) ///
       (D.wpi u1, noconstant noerror), ///
       constraints(1/3) covstate(diagonal)

predict dep*
predict sr*, rstandard
predict sp*, states smethod(onestep) // predicted states
predict sf*, states smethod(filter)  // filtered states
predict sm*, states smethod(smooth)  // smoothed states

outsheet using results_wpi1_ar3_stata.csv, comma


// Example 2: ARIMA model with additive seasonal effects
arima D.ln_wpi, ar(1) ma(1 4)

// Example 3: Multiplicative SARIMA model
use http://www.stata-press.com/data/r12/air2, clear
generate lnair = ln(air)
arima lnair, arima(0,1,1) sarima(0,1,1,12) noconstant

// Example 4: ARMAX model
use http://www.stata-press.com/data/r12/friedman2, clear
arima consump m2 if tin(, 1981q4), ar(1) ma(1)

// Predict - Example 1: Predict, dynamic forecasts
use http://www.stata-press.com/data/r12/friedman2, clear
keep if time<=tq(1981q4)
predict chat, y
predict chatdy, dynamic(tq(1978q1)) y
// Predict - Example 1, part 2: Forecasts
// Note: in the previous example, because `consump`
// was still non-missing for the "out-of-sample" component, it simply
// amounts to in-sample prediction with fixed parameter (that happen
// to have been defined by MLE on a subset of the observations)
// Here make those observations missing so that we get true forecasts.
use http://www.stata-press.com/data/r12/friedman2, clear
keep if time<=tq(1981q4) & time>=tq(1959q1)
arima consump m2 if tin(, 1978q1), ar(1) ma(1)
replace consump = . if time>tq(1978q1)
predict chat, y
predict chatdy, dynamic(tq(1978q1)) y
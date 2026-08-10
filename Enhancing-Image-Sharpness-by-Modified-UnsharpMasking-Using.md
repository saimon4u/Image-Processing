Arabian Journal for Science and Engineering https://doi.org/10.1007/s13369-025-10469-3 

**~~RESEARCH ARTICLE-COMPUTER ENGINEERING AND COMPUTER SCIENCE~~** 



# **Enhancing Image Sharpness by Modified Unsharp Masking Using Coefficient Bounds Obtained for a Subclass of Analytic Functions** 

**B. Aarthy**<sup>**1**</sup> **· B. Srutha Keerthi**<sup>**1**</sup> 

Received: 13 November 2024 / Accepted: 4 July 2025 © King Fahd University of Petroleum & Minerals 2025 

#### **Abstract** 

Image sharpening is a fundamental technique in image processing used to enhance the clarity and detail of images by improving edge contrast. Traditional sharpening methods often introduce artifacts and noise, particularly in low-contrast regions. In this paper, we propose a new approach to image sharpening based on coefficient bounds obtained for a subclass of Sakaguchitype analytic functions subordinate to the generating function of Gregory coefficients. We derive the initial coefficients and incorporate these bounds as adaptive sharpening factors in a modified unsharp masking framework. The proposed method effectively enhances edge definition while preserving the natural appearance of smoother regions. To validate its performance, we apply the technique to various benchmark datasets, including CSIQ, LIVE, TID2013, and KADID 10k, and evaluate sharpness improvement using Pearson linear correlation coefficient and Spearman’s rank ordered correlation coefficient. This study highlights the potential of geometric function theory in advancing image processing techniques and opens new avenues for interdisciplinary research in mathematical imaging. 

**Keywords** Analytic function · Gregory coefficients · Unsharp masking · Image sharpening 

## **1 Introduction** 

Geometric function theory (GFT) can be quite powerful in image processing, especially for tasks that involve shape analysis, image registration, and feature extraction. The Riemann mapping theorem is a fundamental result in complex analysis that states every simply connected, non-empty open subset of the complex plane can be mapped conformally onto the open unit disk. This theorem has several applications in image processing due to its powerful geometric properties. Geometric function theory provides a rich mathematical framework that enhances various aspects of image processing, from feature extraction and enhancement to signal processing and pattern recognition. Its applications help develop sophisticated algorithms that improve the efficiency and effectiveness of image analysis techniques (see [1–3]). 

B B. Srutha Keerthi sruthakeerthi.b@vit.ac.in ; keerthivitmaths@gmail.com B. Aarthy aarthy.b2021@vitstudent.ac.in ; aarthybalaji28@gmail.com 

> 1 Department of Mathematics, School of Advanced Sciences, Vellore Institute of Technology, Chennai 600127, India 

Sharpening refers to methods that are useful for improving intensity transitions in digital images. The perception of boundaries in images is influenced by changes in intensity, the sharper the image, the more smoothly the intensity transitions occur. The clarity of the texture and borders of different specific areas of an image is referred to as image sharpness. This quality has an impact on how information is interpreted, how images are acquired, and how they are processed afterward, particularly in certain applications that require high-quality images. The majority of traditional methods for evaluating image sharpness rely on spectral or spatial domains. The primary means of evaluating an image in the spatial domain is to extract its edge and gradient information. These methods have the benefit of being highly performant in real time and requiring minimal computational work, but they are also susceptible to noise. To extract image frequency information for sharpness evaluation, the spectral domain methods primarily use transformation techniques like wavelet transform and Fourier transform. Although this kind of approach has a significant computational cost, it offers outstanding sensitivity. Deep learning techniques have replaced machine learning techniques as the most popular learning-basedapproachesinrecentyears.Whentwoormore single evaluation techniques are combined in a specific way, 





123 

Arabian Journal for Science and Engineering 

a new method known as a combination method is created. These techniques efficiently increase the accuracy of quality evaluation by combining the benefits of a single method. In order to make visuals sharper, one frequent technique used in graphics is called unsharp masking. 

In image processing, unsharp masking is a commonly used method for sharpening images by boosting contrast along edges and finer details. Unsharp masking, despite its name, operates by removing a blurry copy of the original image from the original itself. By increasing the contrast along edges, this procedure gives an appearance that the edges are sharper. Unsharp masking is a nonlinear method in digital image processing that can be used on color or grayscale images. Although it is a strong technique, it needs to be applied with caution to prevent adding noise or artifacts to the image. In digital photography, satellite imaging, microscopy, and other fields where image sharpness is critical, unsharp masking is frequently employed. Traditional sharpening methods such as high-pass filtering and unsharp masking enhances the contrast of the images but can also add noise and artifacts. This promotes the need for a more mathematically grounded approach to image enhancement that balances edge sharpness while preserving smooth regions. The primary motivation behind our approach is the incorporation of a thorough mathematical framework into image processing, which results in a sharpening technique that: 

- Minimizes Artifacts: Our approach guarantees a regulated enhancement of edges, in contrast to traditional sharpening techniques that may overshoot and result in halo effects. 

- Preserves Image Structure: The coefficient bounds offer a natural method of adjusting sharpening intensity while preserving smooth transitions in areas with low contrast. 

- Bridges Theory and Application: With its potential for practicaluseslikeimageenhancement,thisworkexpands the impact of GFT beyond theoretical research. 

Image sharpening is a crucial technique in various realworld applications, including medical imaging, satellite image analysis, surveillance, and digital photography. In medical imaging, precise edge enhancement is essential for accurate diagnosis, whereas in satellite and remote sensing applications, sharpening improves the detection of geographical features. Autonomous vehicles and surveillance systems rely on real-time image enhancement for object detection, yet computational efficiency is critical. In document processing and Optical Character Recognition (OCR), sharpening aids in enhancing text clarity, improving recognition accuracy for scanned documents. To address these challenges, this study introduces a mathematically rigorous, deterministic sharpening framework based on GFT and Gregory coefficients, 

offering a computationally efficient, interpretable alternative that enhances edge clarity while preserving smooth regions. 

The rest of the article is organized as follows: Section 2 discusses prior research and methods related to image sharpening techniques. Section 3 defines the mathematical concepts including function classes and coefficient bounds. Section 4 explains the image sharpening approach using modified unsharp masking based on the obtained coefficient bounds. Section 5 evaluates the proposed method with datasets and assessment metrics. 

## **2 Related Works** 

This section reviews existing sharpening techniques, focusing on both classical and modern methods. It highlights the limitations of conventional approaches and the need for a more mathematically grounded sharpening framework, such as the proposed method leveraging geometric function theory and coefficient bounds from analytic functions. 

In [4], Bae et. al. determined the Dicrete Cosine Transform (DCT) domain’s weighted average _L_<sup>2</sup> norm, whereas in [5], Bae et. al. also employed DCT blocks to analyze local image characteristics and the qualities of how various kinds of distortion are perceived in terms of visual quality and structural contrast indices. In [6], Gao et. al. proposed a method where the image is represented as a block using a dictionary, and the sparse coefficient is used to calculate the block’s energy. The pooling layer then normalizes the energy of the block to provide a sharpness evaluation score. In [7], to express image localization, a multi-scale spatial max-pooling approach is devised by Lu et. al., and structural information is extracted via Sparse Representation (SR). In [8], Zhang et. al. obtained the saliency maps using Scale-Invariant Feature Transform (SIFT), and shape information is obtained by converting the blocks that compute the gradient maps to DCT coefficients. In [9], Zhan et. al. suggested a method where the distribution of various structural alterations and the degree of structural variations are used to describe the quality of an image. In [10], Bahrami et. al. determined the maximum gradient of the image and change in the gradient. In [11], Gvozden et. al. analyzed the image’s root mean square to understand more about the local contrast. In [12], Bianco et. al. proposed a method which is based on generating generic image descriptions using features taken from pre-trained Convolutional Neural Networks (CNNs). In [13], He et. al. used the image’s numerous characteristics as input, end-to-end training is used to determine the feature weights in order to produce evaluations. In [14], Li et. al. extracted the features using the pre-trained Deep Convolutional Neural Network (DCNN) model, and quality prediction is largely achieved by using least squares regression following feature aggregation. In [15], Zhang et. al. used two convolutional 



123 

Arabian Journal for Science and Engineering 

neural networks to extract features from distorted images, while bilinear pooling is used to predict quality. In [16], Baig et. al. determined the image derivatives and DFT based on blocks. 

In [17], Yang et. al. suggest the RVSIM (Riesz transform and visual contrast sensitivity-based feature SIMilarity index) FR-IQA (full-reference image quality assessment) approach, which combines visual contrast sensitivity with Riesz transform. By utilizing CSF to distribute the weights of various frequency bands, RVSIM fully utilizes the LogGabor filter and MS theory. In [18], Reisenhofer et. al. proposed a Haar wavelet-based perceptual similarity index (HaarPSI), a new and computationally inexpensive metric that produces FR picture quality evaluations is presented. The HaarPSI uses low-frequency Haar wavelet coefficients to weight the significance of (dis)similarities at certain points in the image domain and high-frequency Haar wavelet coefficient magnitudes to identify local similarities. In [19], Jia et. al. calculated weighted standard deviations of the local contrast quality map and the global visual saliency (VS) quality map to produce the final score of the CVSS metric, which is based on the similarity of contrast and VS. In [20], Temel et. al. introduced SUMMER, an algorithm for evaluating image quality that is based on the spectral understanding of multiscale and multi-channel error representations. Also, in [21], Temel et. al. introduced a low-level spatiochromatic-modelbased similarity method (BLeSS), inspired by biology, to support full-reference image quality estimators that initially oversimplify color perception processes. In [22], Nafchi et. al. utilized the image gradient as the primary feature to compute the first similarity map, which is subject to structural deviations. A chromaticity similarity map is then used to quantify color distortions. A suggested deviation pooling technique combines and pools these similarity maps. 

Many existing sharpening techniques, including unsharp masking, high-pass filtering, and advanced edge-preserving methods, often lead to noise amplification and artifacts, especially in low-contrast or smooth regions of an image. This challenge is particularly evident in HDR and low-light images, where variations in contrast and noise levels make sharpening difficult. Since most sharpening methods are not content-aware, they tend to overenhance certain areas unnecessarily, resulting in unnatural image distortions. In fields such as satellite imaging and medical imaging, an intelligent sharpening technique that can differentiate between textured and smooth regions would be highly beneficial. Our proposed approach, which refines unsharp masking using coefficient bounds, addresses these challenges by selectively sharpening the necessary regions while maintaining the natural appearance of smoother areas. This method minimizes oversharpening and prevents excessive noise introduction. 

The motivation for this work arises from the limitations of traditional sharpening methods. While unsharp masking 

and high-pass filtering effectively enhance edges, they often cause overshooting effects and amplify noise, leading to visual artifacts. Wavelet-based methods offer better control but are computationally expensive, and deep learning-based approaches, though adaptive, require extensive training data and high computational resources, making them unsuitable for real-time applications. To overcome these issues, we propose a novel sharpening framework based on geometric function theory. By utilizing the coefficient bounds of the function class ST _�(�, t, λ)_ , our method ensures adaptive edge enhancement while suppressing noise in smooth regions.Thisapproacheffectivelyintegratestheoreticalfunction analysis with practical image processing, offering a controlled sharpening mechanism that improves image clarity without introducing excessive artifacts. 

## **3 Mathematical Framework** 

Let D be the open unit disk defined by D = { _ξ_ ∈ C : | _ξ_ | _<_ 1}. Let _A_ be the set of all functions normalized under the conditions f _(_ 0 _)_ = f<sup>′</sup> _(_ 0 _)_ − 1 = 0 which are analytic and has the Taylor series expansion, 



Let _S_ be the subclass of _A_ which consists of functions that are univalent in D. We say that an analytic function f _(ξ)_ is subordinate to another analytic function _h(ξ)_ , denoted as f _(ξ)_ ≺ _h(ξ)_ , if there exists a Schwarz function _ω(ξ)_ with the conditions, 



such that, 



Furthermore, if _h(ξ)_ is univalent in D, then f _(_ 0 _)_ = _h(_ 0 _)_ and _h(_ D _)_ ⊂ _f (_ D _)_ . 

It is widely known that every function f _(ξ)_ ∈ _S_ has an inverse f<sup>−1</sup> _(ξ)_ defined by, 



and 



Given that f<sup>−1</sup> has an analytic continuation to D, if both f and f<sup>−1</sup> are univalent in D, then the function f is bi-univalent in 



123 

Arabian Journal for Science and Engineering 

D. The bi-univalent function is represented by, 



Some functions including, 



belong to to the class of bi-univalent functions _�_ . The famous Koebe function does not belong to the class _�_ along with other functions, 



In 1967, Lewin [23] investigated the class _�_ and provided the result | _a_ 2| _<_ 1 _._ 51. Thereafter, Brannan, David, and Clunie [24] presumed that | _a_ 2| _<_ √2. Finding the coefficient estimates | _an_ | for _n_ ≥ 3 for the Taylor Maclaurin series is still a conjecture. Ma and Minda [25] unified different classes of starlike and convex functions where either of the quantities _<u>ξ</u>_ <u>f</u><sup>′</sup> _<u>(ξ)</u>_<sup>_<u>ξ</u>_</sup><sup><u>f′′</u></sup><sup>_<u>(ξ)</u>_</sup> f _(ξ)_<sup>or 1 +</sup> f<sup><u>′</u></sup> _(ξ)_<sup>is subordinate to a more general analytic</sup> function _φ_ ∈ _P_ with the conditions _φ(_ 0 _)_ = 1 and _φ_<sup>′</sup> _(_ 0 _) >_ 0 and _φ_ maps D onto a region starlike with respect to 1 and symmetric with respect to the real axis. They introduced the following classes of functions: 



and 



which are considered as the most essential subclasses of starlike and convex functions where _φ(ξ)_ =<sup>_<u>(</u>_</sup> _(_<sup>1</sup> 1<sup><u>+</u></sup> −<sup>_<u>ξ)</u>_</sup> _ξ)_<sup>. Many results</sup> have been obtained regarding the functions of the class _�_ (see [26–32]). 

Consider the Maclaurin series, 



where _�n_ are called the Gregory coefficients or reciprocal logarithmic numbers or Bernoulli numbers of the second kind or Cauchy numbers of the first kind (see [33, 34]). 

Figure 1 gives the graphical representation of the generating function of G _(ξ)_ . Gregory coefficients arise in numerical analysis, particularly in the Gregory series, which improves numerical integration and summation methods by incorporating higher-order corrections. These coefficients appear in the Gregory quadrature formula, refining the trapezoidal rule by adding terms derived from finite differences. They play a crucial role in the Euler-Maclaurin formula, which bridges discrete summation and continuous integration using Bernoulli numbers. By adjusting approximations, Gregory coefficients enhance numerical integration, finite difference methods, and asymptotic series expansions, making them essential in computational mathematics. 

In [35], Murugusundaramoorthy et. al. considered three subclasses of analytic bi-univalent functions subordinate to the generating function of Gregory coefficients and obtained the initial coefficient bounds | _a_ 2| and | _a_ 3| along with the Fekete Szego inequality. Also, in [36], Murugusundaramoorthy et. al. considered the class of starlike functions subordinate to Gregory coefficients and obtained the bound | _an_ | for _n_ = 2 _,_ 3 _,_ 4 _,_ 5 _,_ 6 inclusive of the logarithmic and inverse coefficient bounds for the same class. In [37], Srivastava et. al. obtained the first five sharp coefficient bounds for the class of convex functions subordinate to the generating function of the Gregory coefficients. Motivated by the aforementioned results, in this paper, we introduce a new subclass of Sakaguchi-type analytic functions subordinate to the generating function whose coefficients are Gregory numbers _�n_ . 

Let _P_ represent the set of all functions _p(ξ)_ which are analytic in the open unit disk D such that _p(ξ)_ takes the value 1 at _ξ_ = 0 and the real part of _p_ remains positive, i.e., Re{ _p(ξ)_ } _>_ 0. 

**Lemma 1** _[38] If p_ ∈ _P has the form p(ξ)_ = 1 + _c_ 1 _ξ_ + _c_ 2 _ξ_<sup>2</sup> + · · · _, ξ_ ∈ D _, then,_ 



_and this inequality is sharp for each n_ ∈ N _._ 

The above lemma is famously known as the Carathéodory lemma (see [38–40]). In geometric function theory, Carathéodory’s lemma is used to study functions subordinate to analytic functions with positive real parts. It plays a role in proving coefficient bounds, distortion theorems, and growth estimates for subclasses of univalent and close-toconvex functions. 

**Definition 1** A function f _(ξ)_ ∈ _�_ is said to be in the class ST _�(�, t, λ)_ if it satisfies the following subordination: 





123 



<!-- Start of picture text -->
—— 0.5 <<<br>0.8 | aN 0.4 — —*<br>0.6 / \ 0.3 é \<br>0.4 / \ : : 0.2 / \<br>0.2 / \ (8) ~ log(1+®) 0.1 t SA }<br>7 | :<br>0.2 \ 0.1} j<br>0.4 \ / 0.2 NY<br>06 f f- 0.3 : f-<br>0.8 — y 0.4 —_— La<br>= Se ns -0.5 re el<br>At 0.5 0 0.5 1 0.2 0.4 0.6 0.8 1 1.2 1.4<br>Unit disk in §—plane Image of unit disk in w — plane<br><!-- End of picture text -->



<!-- Start of picture text -->
(peace<br>ey<br><!-- End of picture text -->

Arabian Journal for Science and Engineering 

from which we obtain 



Then, 



Moreover, on subtracting (28) from (26), 



Substituting (25) in the place of _a_ 2<sup>2and applying Lemma 1,</sup> 



The proof of our theorem is now complete. ⊓⊔ 

## **4 Proposed Work** 

From Eqs.(16) and (23), 



Comparing the coefficients, 





From (25) and (27), 



and 



This section provides a detailed explanation of the unsharp masking process used to sharpen blurred images, utilizing the coefficients derived for the class ST _�(�, t, λ)_ as presented in Theorem 1. 

### **4.1 Unsharp Masking** 

Unsharp masking typically involves two main steps. First, the original image is smoothed using a high-pass filter to extract an edge image, also referred to as a mask. In the second step, this edge image is added to the blurred version of the original image to enhance sharpness. Figure 2 illustrates the flowchart of the proposed methodology, where _(_ − _)_ denotes the subtraction of the smoothed image from the original to obtain the edge image, _(_ ∗ _)_ signifies the application of the sharpness factor (coefficient bounds) to adjust the enhancement, and _(_ + _)_ represents the addition of the edge image to the blurred image, resulting in the final sharpened output. 

The coefficient bounds obtained from (32) and (34) for different values of _t_ and _λ_ are experimented with the images to attain maximum sharpening of the images. Based on experimental results, the best balance was observed at _t_ = 0 _._ 6 and _λ_ = 0, where the sharpening effect was strong enough to enhance edges but without causing excessive artifacts. 

Adding (26) and (28) and substituting (30), 





By using triangle inequality and Lemma 1, 



(32) 



123 



<!-- Start of picture text -->
Original Image Smo octhed image<br>' NAYKE& s Y é Gaussian ' Nhé .<br>TRING. Smoothing a<br>SNe =<br>ins ee<br>r “aaa arerererrererrerererrererereree wkspen ! Enhanced Eoge image<br>''<br>'!<br>'!<br>'Coefficient Bounds for ;<br>.' the class *k ——- '<br>'1<br>''<br>' 1<br>BWeeeweeaeeweeweeewaeeeeaeaeeaeaeeaeaeaeaeaaeae @ @ @ @ @ ot<br>+<br>Sharpened image orslomage<br>5 ’ f ‘<br>Se a «<br><!-- End of picture text -->

(peace WY 



<!-- Start of picture text -->
} Nii ap a 43 et 3 — - ryt<br><!-- End of picture text -->



<!-- Start of picture text -->
Ay dol Wee<br><!-- End of picture text -->



<!-- Start of picture text -->
| | all “<br><!-- End of picture text -->



<!-- Start of picture text -->
: Ve os e= = S ~<br>Re PC ie NG < < > \ \ | :<br>= =teY Ny [ | \<br><!-- End of picture text -->

Leen 

Arabian Journal for Science and Engineering 



**Fig. 7** Sharpening of various images from CSIQ dataset at different blur levels 



123 

Arabian Journal for Science and Engineering 



**Fig. 8** Sharpening of various images from LIVE dataset at different blur levels 

assessment metrics tailored to sharpened images is an emergtrates its primary application in accuracy calculation. ing area that could help improve algorithm evaluation and development. 

The correlation between the algorithm evaluation value and the human subjective score is expressed by the Pearson linear correlation coefficient (PLCC). Equation (36) illus- 





123 

Arabian Journal for Science and Engineering 



**Fig. 9** Sharpening of various images from TID2013 dataset at different blur levels 

where _α_ ¯ and _β_<sup>¯</sup> are the means of _αi_ and _βi_ , respectively, and _σα_ and _σβ_ are the corresponding standard deviations of _αi_ and _βi_ . 

The monotonicity of algorithm prediction is primarily assessed using Spearman’s rank ordered correlation coefficient (SROCC) as given in equation (37). 



where the sorting locations of _xi_ and _yi_ in each of the corresponding data sequences are denoted by _γxi_ and _γyi_ . 

In this paper, we have selected the metrics PLCC and SROCC to compare the proposed methods with other methods in the literature. 

## **5 Experimental Results and Analysis** 

The proposed image sharpening method utilizing unsharp masking was evaluated through a systematic analysis of its effectiveness in enhancing image quality. The analysis aimed to quantify improvements in sharpness and detail across various types of images, employing both visual assessment and quantitative metrics, including Pearson linear correlation coefficient (PLCC) and Spearman’s rank ordered correlation coefficient (SROCC). 

To observe the performance of the proposed method, PLCC and SROCC are employed. The experimental results presented in Table 1 and Table 2 were obtained from the cited references, and the same datasets were used for testing each comparative method group [46]. The experiments for the proposed method are done using MATLAB online. 



123 



<!-- Start of picture text -->
° ~~, = S 5 DL ZB LDQODX\\_ BZ T GN<br>7 “4 3 \ Segal & | IQ) GH — 233 har Vy,—~ 33 PAN<br>Il > mT 1)))))) mT A))))) T))))))) ee mTT3)))))<br>_ iy) any) ay) ayy)<br>‘< i 4 salty v tally \ tay iY tly<br>at = tt% "wy = t&% My, - attY Ny, » =teY Wy /<br>QPSPAPO ZSWW 22 \\0@WWCVD°loyOOXxk ARO, BY  \—°\ 2 ddRaW <wwWw<br>4 ” - , ’<br>Iv My, ¥Fma Uy, YFSa Uy, FY) f WY \\ Wy, SYoe Se \ Wy,( SF) fi A<br>\a)\f‘eetiN  NSIA ltON Naa 9) vy  NN)NN)i\ FieyANY! \¢Ne THANN)} 44\ 1)jyl"<br>_ ae 4, a4) a aA 4 a4 , a4<br>. :<br>(a) (b) (c) (d) (e)<br><!-- End of picture text -->

x(A, 

>, 

Arabian Journal for Science and Engineering 

**Table 1** Comparison of PLCC and SROCC of the proposed method with other methods 

|Method|LIVE||CSIQ||TID2013||
|---|---|---|---|---|---|---|
||PLCC|SROCC|PLCC|SROCC|PLCC|SROCC|
|DCT-QM [4]|0.925|0.938|0.872|0.926|0.852|0.854|
|SC-QI [5]|0.937|0.948|0.927|0.943|0.907|0.905|
|SPARISH [6]|0.956|0.959|0.938|0.914|0.900|0.893|
|SR [7]|0.961|0.955|0.950|0.921|0.899|0.892|
|RFSV [8]|0.974|0.971|0.942|0.920|0.924|0.932|
|SVC [9]|0.949|0.941|0.952|0.954|0.857|0.787|
|MGV [10]|0.960|0.963|0.907|0.950|0.914|0.921|
|BISHARP [11]|0.952|0.960|0.942|0.927|0.892|0.896|
|DeepBIQ [12]|0.912|0.893|0.975|0.967|0.920|0.922|
|MSFF [13]|0.949|0.950|–|–|0.917|0.922|
|SFA [14]|0.942|0.953|–|–|0.954|0.948|
|DB-CNN [15]|0.970|0.968|0.959|0.946|0.865|0.816|
|FISH [16]|0.904|0.841|0.923|0.894|0.911|0.912|
|Proposed|0.945|0.945|0.952|0.951|0.888|0.900|



mance, and quality of various image processing methods and algorithms. Quantitative evaluation offers objective, reproducible metrics that are particularly helpful in fields like computer vision, medical imaging, and photography where accurate measurements of image quality are essential, in contrast to qualitative (visual) evaluations that depend on subjective judgment. 

Table 1 presents the average PLCC and SROCC values for the proposed method, along with a comparative analysis against other image sharpening algorithms from the literature. Since utilizing coefficient bounds from the subclass of analytic functions ST _�(�, t, λ)_ subordinate to the generating function of Gregory coefficients is still an emerging approach, our method achieves correlation metrics closer to 1. Given that correlation values range from −1 (negative correlation) to +1 (positive correlation), with 0 indicating no correlation, achieving values near +1 is a desirable outcome for a novel technique like the one proposed. Additionally, Table 2 provides a comparison of the average PLCC and SROCC values for the proposed method against existing techniques in the literature for the KADID 10k dataset. 

From Figures 7, 8, 9, and 10, it is evident that the proposed method, which utilizes coefficient bounds as sharpening factors in unsharp masking, yields effective results. While other state-of-the-art techniques also demonstrate strong performance, this study highlights the proposed approach due to its foundation in geometric function theory, a developing strategy in image processing. Overall, incorporating coefficient bounds in image sharpening presents a promising avenue for enhancing image quality across various applications, including digital photography, medical imaging, and video processing. 

**Table 2** Comparison of PLCC and SROCC for KADID 10k dataset 

|Method|PLCC|SROCC|
|---|---|---|
|BLeSS [21]|0.780|0.952|
|CVSS [19]|0.884|0.957|
|HaarPSI [18]|0.908|0.952|
|MDSI [22]|0.948|0.950|
|RVSIM [17]|0.941|0.939|
|SUMMER [20]|0.864|0.950|
|Proposed|0.915|0.910|



### **5.3 Discussion** 

The experimental results, evaluated using Pearson linear correlation coefficient (PLCC) and Spearman’s rank ordered correlation coefficient (SROCC), demonstrate that our proposed method achieves competitive performance in sharpening quality across multiple benchmark datasets. The proposed method applies sharpening in a controlled manner preserving fine details without causing over enhancement. The observed correlation metrics confirm that the proposed technique competes well with state-of-the-art sharpening algorithms. Unlike traditional unsharp masking, which applies a uniform sharpening factor, our approach adapts sharpening intensity using coefficient bounds derived from geometric function theory, ensuring a balance between edge enhancement and noise suppression. 

### **5.4 Limitation** 

One limitation observed is that for images with extremely high blur levels, although the sharpening effect is notice- 



123 

Arabian Journal for Science and Engineering 

able, slight hazing can appear in the output, particularly in texture-rich regions. This may explain the marginally lower PLCC and SROCC values compared to some stateof-the-art learning-based methods. Furthermore, the discrete nature of digital images introduces challenges when applying continuous mathematical function theory, requiring careful numerical implementation. 

## **6 Conclusion** 

Unsharp masking is a simple yet effective method for improving image sharpness. The image appears sharper by enhancing edges and minute details by eliminating a blurry version of the image from the original image. But extreme caution must be taken to prevent oversharpening, which can result in artifacts and a loss of natural appearance. Due to its simplicity of usage and efficiency in enhancing image quality, unsharp masking is extensively employed in a variety of applications, such as digital image processing, medical imaging, and photography. In this article, a modified unsharp masking using coefficient bounds obtained for a subclass of analytic functions subordinate to Gregory coefficients is utilized for improving the sharpness of the image. Future research will examine how to improve this technique even further and apply it in new applications, potentially expanding its advantages to other fields where image quality is crucial. 

**Acknowledgements** The authors sincerely thank the editor and the anonymous reviewers for their valuable comments and suggestions to improve the article in its present form. 

**Author Contributions** All authors have jointly worked and agreed for the manuscript. 

**Funding** No fund was received for this article. 

**Data Availability** The following links are provided to download the datasets used for this study. Link for CSIQ dataset. Link for LIVE dataset. Link for TID2013 dataset Link for KADID 10k dataset 

### **Declarations** 

## **References** 

1. Aarthy, B.; Keerthi, B.S.: Enhancement of various images using coefficients obtained from a class of Sakaguchi type functions. Sci. Rep. **13** (1), 18722 (2023) 

2. Nithiyanandham, E.K.; Srutha Keerthi, B.: A new proposed model for image enhancement using the coefficients obtained by a sub- 

   - class of the Sakaguchi-type function. Signal, Image Video Process. **18** (2), 1455–1462 (2024) 

3. Sundari, K.S.; Keerthi, B.S.: Enhancing the quality of lowlight images via the coefficient bounds derived for a subclass of Sakaguchi-type function. EURASIP J. Image Video Process. **2025** (1), 4 (2025) 

4. Bae, S.H.; Kim, M.: DCT-QM: A DCT-based quality degradation metricforimagequalityoptimizationproblems.IEEETrans.Image Process. **25** (10), 4916–4930 (2016) 

5. Bae, Sung-Ho.; Kim, Munchurl: A novel image quality assessment with globally and locally consilient visual quality perception. IEEE Trans. Image Process. **25** (5), 2392–2406 (2016) 

6. Gao, F.; Jun, Y.; Zhu, S.; Huang, Q.; Tian, Q.: Blind image quality prediction by exploiting multi-level deep representations. Pattern Recognit. **81** , 432–442 (2018) 

7. Qingbo, L.; Zhou, W.; Li, H.: A no-reference image sharpness metric based on structural information using sparse representation. Inf. Sci. **369** , 334–346 (2016) 

8. Zhang, S.; Li, P.; Xianghua, X.; Li, L.; Chang, C.C.: No-reference image blur assessment based on response function of singular values. Symmetry **10** (8), 304 (2018) 

9. Zhan, Y.; Zhang, R.; Qian, W.: A structural variation classification model for image quality assessment. IEEE Trans. Multimed. **19** (8), 1837–1847 (2017) 

10. Bahrami, K.; Kot, A.C.: A fast approach for no-reference image sharpness assessment based on maximum local variation. IEEE Signal Process. Lett. **21** (6), 751–755 (2014) 

11. Gvozden, G.; Grgic, S.; Grgic, M.: Blind image sharpness assessment based on local contrast map statistics. J. Vis. Commun. Image Represent. **50** , 145–158 (2018) 

12. Bianco, S.; Celona, L.; Napoletano, P.; Schettini, R.: On the use of deep learning for blind image quality assessment. Signal, Image Video Process. **12** , 355–362 (2018) 

13. He, S.; Liu, Z.: Image quality assessment based on adaptive multiple skyline query. Signal Process.: Image Commun. **80** , 115676 (2020) 

14. Li, D.; Jiang, T.; Lin, W.; Jiang, M.: Which has better visual quality: Theclearblueskyorablurryanimal?IEEETrans.Multimed. **21** (5), 1221–1234 (2018) 

15. Zhang,W.;Ma,K.;Yan,J.;Deng,D.;Wang,Z.:Blindimagequality assessment using a deep bilinear convolutional neural network. IEEE Trans. Circuits Syst. Video Technol. **30** (1), 36–47 (2018) 

16. Baig, Md..A.; Moinuddin, A.A.; Khan, E.; Ghanbari, M.: DFTbased no-reference quality assessment of blurred images. Multimed. Tools Appl. **81** (6), 7895–7916 (2022) 

17. Yang, G.; Li, D.; Fan, L.; Liao, Y.; Yang, W.: RVSIM: a feature similarity method for full-reference image quality assessment. EURASIP J. Image Video Process. **1–15** , 2018 (2018) 

18. Reisenhofer, R.; Bosse, S.; Kutyniok, G.; Wiegand, T.: A Haar wavelet-based perceptual similarity index for image quality assessment. Signal Process.: Image Commun. **61** , 33–43 (2018) 

19. Jia,H.;Zhang,L.;Wang,T.:Contrastandvisualsaliencysimilarityinduced index for assessing image quality. IEEE Access **6** , 65885– 65893 (2018) 

20. Temel, D.; AlRegib, G.: Perceptual image quality assessment through spectral analysis of error representations. Signal Process.: Image Commun. **70** , 37–46 (2019) 

21. Temel, D.; AlRegib, G.: BLeSS: bio-inspired low-level spatiochromatic similarity assisted image quality assessment. In: 2016 IEEE International Conference on Multimedia and Expo (ICME), pp. 1–6. IEEE (2016) 

22. Nafchi, H.Z.; Shahkolaei, A.; Hedjam, R.; Cheriet, M.: Mean deviation similarity index: efficient and reliable full-reference image quality evaluator. IEEE Access **4** , 5579–5590 (2016) 

23. Lewin, M.: On a coefficient problem for bi-univalent functions. Proc. Am. Math. Soc. **18** (1), 63–68 (1967) 



123 

Arabian Journal for Science and Engineering 

24. Brannan, D.A.; Clunie, J. et al. Aspects of contemporary complex analysis (1980) 

25. Ma, W.: A unified treatment of some special classes of univalent functions. In: Proceedings of the Conference on Complex Analysis, 1992. International Press Inc. (1992) 

26. Srivastava, H.M.; Eker, S.S.; Ali, R.M.: Coefficient bounds for a certain class of analytic and bi-univalent functions. Filomat **29** (8), 1839–1843 (2015) 

27. Frasin, B.A.; Aouf, M.K.: New subclasses of bi-univalent functions. Appl. Math. Lett. **24** (9), 1569–1573 (2011) 

28. Murugusundaramoorthy, G.; Magesh, N.; Prameela, V.; et al. Coefficient bounds for certain subclasses of bi-univalent function. In: Abstract and Applied Analysis, vol 2013. Hindawi (2013) 

29. Adegani, E.A.; Jafari, M.; Bulboac˘a, T.; Zaprawa, P.: Coefficient bounds for some families of bi-univalent functions with missing coefficients. Axioms **12** (12), 1071 (2023) 

30. Al-Rawashdeh, W.: Coefficient bounds of a class of bi-univalent functions related to Gegenbauer polynomials. Int. J. Math. Comput. Sci. **19** (3), 635–642 (2024) 

31. Sharma, P.; Sivasubramanian, S.; Cho, N.E.: Initial coefficient bounds for certain new subclasses of bi-univalent functions with bounded boundary rotation. AIMS Math **8** , 29535–29554 (2023) 

32. Khan, B.; Srivastava, H.M.; Tahir, M.; Darus, M.; Ahmad, Q.Z.; Khan, N.: Applications of a certain q-integral operator to the subclasses of analytic and bi-univalent functions. AIMS Math **6** , 1024–1039 (2021) 

33. Phillips, G.M.: Gregory’s method for numerical integration. Am. Math. Mon. **79** (3), 270–274 (1972) 

34. Berezin, I.S.; Zhidkov, N.P.: Computing Methods: Adiwes International Series in the Engineering Sciences, vol 1. Elsevier (2014) 

40. Duren,P.L.:Univalentfunctions,vol259.SpringerScience&Business Media (2001) 

41. Larson, E.C.; Chandler, D.M.: Most apparent distortion: fullreference image quality assessment and the role of strategy. J. Electron. Imaging **19** (1), 011006–011006 (2010) 

42. Sheikh, H.R.; Sabir, M.F.; Bovik, A.C.: A statistical evaluation of recent full reference image quality assessment algorithms. IEEE Trans. Image Process. **15** (11), 3440–3451 (2006) 

43. Ponomarenko, N.; Jin, L.; Ieremeiev, O.; Lukin, V.; Egiazarian, K.; Astola, J.; Vozel, B.; Chehdi, K.; Carli, M.; Battisti, F., et al.: Image database tid2013: Peculiarities, results and perspectives. Signal Process.: Image Commun. **30** , 57–77 (2015) 

44. Lin, H.; Hosu, V.; Saupe, D.: KADID-10k: a large-scale artificially distorted IQA database. In: 2019 10th International Conference on Quality of Multimedia Experience (QoMEX), pp. 1–3. IEEE (2019) 

45. Lin, H.; Hosu, V.; Saupe, D.: DEEPFL-IQA: weak supervision for deep IQA feature learning. arXiv preprint arXiv:2001.08113, (2020) 

46. Mengqiu, Z.; Lingjie, Y.; Wang, Z.; Ke, Z.; Zhi, C.: A survey on objective evaluation of image sharpness. Appl. Sci. **13** (2), 2652 (2023) 

Springer Nature or its licensor (e.g. a society or other partner) holds exclusive rights to this article under a publishing agreement with the author(s) or other rightsholder(s); author self-archiving of the accepted manuscript version of this article is solely governed by the terms of such publishing agreement and applicable law. 

35. Murugusundaramoorthy, G.; Vijaya, K.; Bulboac˘a, T.: Initial coefficient bounds for bi-univalent functions related to Gregory coefficients. Mathematics **11** (13), 2857 (2023) 

36. Kazımo˘glu, S.; Deniz, E.; Srivastava, H.M.: Sharp coefficients bounds for starlike functions associated with Gregory coefficients. Complex Anal. Op. Theory **18** (1), 6 (2024) 

37. Srivastava, H.M.; Cho, N.E.; Alderremy, A.A.; Lupas, A.A.; Mahmoud, E.E.: Khan, Shahid: Sharp inequalities for a class of novel convex functions associated with Gregory polynomials. J. Inequal. Appl. **2024** (1), 140 (2024) 

38. Carathéodory, C.: Über den variabilitätsbereich der koeffizienten von potenzreihen, die gegebene werte nicht annehmen. Math. Ann. **64** (1), 95–115 (1907) 

39. Pommerenke, C.: Univalent functions. Vandenhoeck and Ruprecht (1975) 



123 


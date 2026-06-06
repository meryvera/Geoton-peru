<StyledLayerDescriptor version="1.0.0" xmlns="http://www.opengis.net/sld" xmlns:gml="http://www.opengis.net/gml" xmlns:ogc="http://www.opengis.net/ogc" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/sld http://schemas.opengis.net/sld/1.0.0/StyledLayerDescriptor.xsd">
  <NamedLayer>
    <Name>sld_peru_infraestructura_loc_esc_pron_feb2022</Name>
    <UserStyle>
      <FeatureTypeStyle>
        <Rule>
          <Name>OPERATIVO</Name>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>cod_estado</ogc:PropertyName>
              <ogc:Literal>1</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <PointSymbolizer>
             <Graphic>
               <Mark>
                 <WellKnownName>circle</WellKnownName>
                 <Fill>
                   <CssParameter name="fill">#b533ff</CssParameter>
                 </Fill>
                  <Stroke>
                    <CssParameter name="stroke">#4c0073</CssParameter>
                    <CssParameter name="stroke-width">1.00</CssParameter>
           		 </Stroke>
               </Mark>
               <Size>8</Size>
             </Graphic>
 			</PointSymbolizer>
        </Rule>
        <Rule>
          <Name>NO OPERATIVO</Name>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>cod_estado</ogc:PropertyName>
              <ogc:Literal>2</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
           <PointSymbolizer>
             <Graphic>
               <Mark>
                 <WellKnownName>circle</WellKnownName>
                 <Fill>
                   <CssParameter name="fill">#e1abff</CssParameter>
                 </Fill>
                  <Stroke>
                    <CssParameter name="stroke">#4c0073</CssParameter>
                    <CssParameter name="stroke-width">1.00</CssParameter>
           		 </Stroke>
               </Mark>
               <Size>8</Size>
             </Graphic>
 			</PointSymbolizer>
        </Rule>
        <Rule>
           
   <MaxScaleDenominator>300000</MaxScaleDenominator>
        <TextSymbolizer>
<Label><ogc:PropertyName>nom_loc_es</ogc:PropertyName></Label>
<Font>

<CssParameter name="font-family">Verdana</CssParameter>
<CssParameter name="font-size">8</CssParameter>
    <CssParameter name="font-weight">bold</CssParameter>
</Font>
<LabelPlacement>
<PointPlacement>
<AnchorPoint>
<AnchorPointX>-0.1</AnchorPointX>
<AnchorPointY>0.5</AnchorPointY>
</AnchorPoint>
</PointPlacement>
</LabelPlacement>
     <Halo>
        <Radius>1.5</Radius>
        <Fill>
            <CssParameter name="fill">#ffffff</CssParameter>
          
        </Fill>
</Halo>     
<Fill>
<CssParameter name="fill">#4c0073</CssParameter>
</Fill>
          
</TextSymbolizer>
</Rule>
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>